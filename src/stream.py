"""Replay saved rover frames as a live camera feed, with optional fault injection."""

import os
import time

import numpy as np
from PIL import Image, ImageFilter

from src.config import FRAMES_DIR

FAULTS = ["none", "blur", "dark", "overexposed", "corrupt", "drop"]


def list_frames(folder=FRAMES_DIR):
    """Sorted list of image paths in the demo folder (label files excluded)."""
    if not os.path.isdir(folder):
        return []
    names = []
    for name in sorted(os.listdir(folder)):
        if name.lower().endswith((".jpg", ".png")) and not name.endswith("_label.png"):
            names.append(os.path.join(folder, name))
    return names


def label_path(frame_path):
    """Path of the ground-truth label saved next to a demo frame, if any."""
    base = os.path.splitext(frame_path)[0]
    path = base + "_label.png"
    if os.path.exists(path):
        return path
    return None


def load_frame(path):
    try:
        return Image.open(path).convert("L")
    except Exception:
        return None


def inject_fault(image, fault):
    """Return a damaged copy of the frame, or None if the frame is dropped."""
    if fault == "drop":
        return None
    if fault == "blur":
        return image.filter(ImageFilter.GaussianBlur(radius=8))
    if fault == "dark":
        return Image.fromarray((np.asarray(image, dtype=np.float32) * 0.05).astype(np.uint8))
    if fault == "overexposed":
        return Image.fromarray(np.clip(np.asarray(image, dtype=np.float32) * 4 + 120, 0, 255).astype(np.uint8))
    if fault == "corrupt":
        arr = np.asarray(image, dtype=np.float32).copy()
        arr[::3, :] = np.nan
        return arr
    return image


def make_packet(seq, path, fault="none"):
    """One frame as it would arrive from the rover: sequence number, time, image (or None if lost)."""
    image = load_frame(path)
    if image is not None:
        image = inject_fault(image, fault)
    return {"seq": seq, "timestamp": time.time(), "source": os.path.basename(path), "image": image, "fault": fault}
