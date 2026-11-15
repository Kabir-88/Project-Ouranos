"""Project Ouranos dashboard: live terrain hazard detection on a Mars rover camera feed.

Run: streamlit run app.py
"""

import json
import os
import time

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

from src.config import MODEL_PATH, METRICS_PATH, CLASS_NAMES, CLASS_COLOURS, UNKNOWN_COLOUR, NULL_LABEL, IMG_SIZE
from src.inference import analyse_frame, overlay
from src.stream import FAULTS, list_frames, label_path, make_packet
from src.traverse import assess_path, blocked_decision, path_region

st.set_page_config(page_title="Project Ouranos", layout="wide")

DECISION_COLOURS = {"GO": "#2e9e5b", "CAUTION": "#d9a400", "STOP": "#d23c3c", "HOLD": "#5a5ad2"}


@st.cache_resource
def get_model():
    if not os.path.exists(MODEL_PATH):
        return None
    from src.model import load_model
    return load_model(MODEL_PATH)


def draw_path_box(rgb):
    """Outline the region the rover will drive over."""
    out = rgb.copy()
    mask = path_region(out.shape[:2])
    rows = np.where(mask.any(axis=1))[0]
    cols = np.where(mask.any(axis=0))[0]
    top, bottom, left, right = rows[0], rows[-1], cols[0], cols[-1]
    out[top, left:right + 1] = (255, 255, 255)
    out[bottom, left:right + 1] = (255, 255, 255)
    out[top:bottom + 1, left] = (255, 255, 255)
    out[top:bottom + 1, right] = (255, 255, 255)
    return out


def label_overlay(gray, path):
    """Colour the ground-truth label (from the expert test set) for comparison."""
    label = np.asarray(Image.open(path).resize((IMG_SIZE, IMG_SIZE), Image.NEAREST))
    if label.ndim == 3:
        label = label[:, :, 0]
    classes = label.astype(int)
    classes[label == NULL_LABEL] = -2
    return overlay(gray, classes)


def init_state():
    defaults = {"index": 0, "seq": 0, "log": [], "pending_fault": "none",
                "received": 0, "dropped": 0, "bad": 0, "playing": False}
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def log(message):
    stamp = time.strftime("%H:%M:%S")
    st.session_state.log.insert(0, stamp + "  " + message)
    st.session_state.log = st.session_state.log[:20]


init_state()
model = get_model()
frames = list_frames()

st.title("Project Ouranos")
st.caption("Terrain hazard detection for Mars rover driving. Real Curiosity NAVCAM frames, AI4Mars labels.")

if model is None:
    st.error("No trained model found at models/terrain_unet.keras. Train it with notebooks/train_kaggle.ipynb and copy the file into models/.")
    st.stop()
if len(frames) == 0:
    st.error("No demo frames found in demo_frames/. The training notebook exports them.")
    st.stop()

# ----- Sidebar controls -----
with st.sidebar:
    st.header("Rover feed")
    speed = st.slider("Seconds per frame", 0.5, 5.0, 2.0, 0.5)
    col_a, col_b = st.columns(2)
    if col_a.button("Play" if not st.session_state.playing else "Pause", width="stretch"):
        st.session_state.playing = not st.session_state.playing
    step = col_b.button("Next frame", width="stretch")
    show_truth = st.checkbox("Show expert label (if available)", value=False)

    st.header("Fault injection")
    fault = st.selectbox("Fault", FAULTS[1:])
    if st.button("Inject on next frame", width="stretch"):
        st.session_state.pending_fault = fault
        log("Operator queued fault: " + fault)

    st.header("Link status")
    st.metric("Frames received", st.session_state.received)
    st.metric("Frames lost", st.session_state.dropped)
    st.metric("Unusable frames", st.session_state.bad)

    if os.path.exists(METRICS_PATH):
        st.header("Model test results")
        with open(METRICS_PATH) as f:
            metrics = json.load(f)
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                st.write(key + ": " + str(round(value, 3)))

# ----- Advance the feed -----
advance = step or st.session_state.playing
if advance:
    st.session_state.index = (st.session_state.index + 1) % len(frames)
    st.session_state.seq += 1

path = frames[st.session_state.index]
fault_now = st.session_state.pending_fault if advance else "none"
packet = make_packet(st.session_state.seq, path, fault_now)
if advance:
    st.session_state.pending_fault = "none"

# ----- Analyse -----
if packet["image"] is None:
    if advance:
        st.session_state.dropped += 1
        log("Frame " + str(packet["seq"]) + " lost in transmission. Holding position.")
    result = None
    decision = blocked_decision(["frame lost"])
else:
    result = analyse_frame(model, packet["image"])
    if result["classes"] is None or result["problems"]:
        decision = blocked_decision(result["problems"])
    else:
        decision = assess_path(result["classes"])
    if advance:
        st.session_state.received += 1
        if decision["decision"] == "HOLD":
            st.session_state.bad += 1
        log("Frame " + str(packet["seq"]) + ": " + decision["decision"]
            + ((" - " + "; ".join(decision["reasons"])) if decision["reasons"] else ""))

# ----- Display -----
left, right = st.columns([3, 2])
with left:
    st.subheader("Camera frame " + str(packet["seq"]) + "  (" + packet["source"] + ")")
    if result is None:
        st.warning("No frame received.")
    else:
        img_cols = st.columns(2)
        img_cols[0].image((result["gray"] * 255).astype(np.uint8), caption="Raw NAVCAM frame", width="stretch")
        if result["classes"] is not None:
            img_cols[1].image(draw_path_box(overlay(result["gray"], result["classes"])),
                              caption="Model terrain map (box = path ahead)", width="stretch")
        if show_truth and label_path(path) is not None and result["classes"] is not None:
            st.image(label_overlay(result["gray"], label_path(path)), caption="Expert label (grey = unlabelled)", width=300)

    legend = ""
    for name, rgb in zip(CLASS_NAMES + ["unknown"], CLASS_COLOURS + [UNKNOWN_COLOUR]):
        legend += "<span style='background:rgb" + str(rgb) + ";padding:2px 8px;margin-right:6px;border-radius:4px;color:white'>" + name + "</span>"
    st.markdown(legend, unsafe_allow_html=True)

with right:
    colour = DECISION_COLOURS[decision["decision"]]
    st.markdown("<div style='background:" + colour + ";color:white;padding:18px;border-radius:10px;"
                "font-size:32px;text-align:center'>" + decision["decision"] + "</div>", unsafe_allow_html=True)
    st.metric("Path risk", str(round(decision["risk"] * 100)) + "%")
    for reason in decision["reasons"]:
        st.write("- " + reason)
    if decision["fractions"]:
        chart = pd.DataFrame({"percent of path": [v * 100 for v in decision["fractions"].values()]},
                             index=list(decision["fractions"].keys()))
        st.bar_chart(chart, horizontal=True)

    st.subheader("Event log")
    st.code("\n".join(st.session_state.log) if st.session_state.log else "No events yet.")

if st.session_state.playing:
    time.sleep(speed)
    st.rerun()
