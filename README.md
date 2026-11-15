# Project Ouranos

**Terrain hazard detection for Mars rovers: spot sand and rocks before the wheels do.**

*Praemonitus, praemunitus.* Forewarned is forearmed.

## Problem

Getting stuck has ended real Mars missions. Spirit became trapped in soft sand in 2009 and never drove free.
Curiosity's wheels were damaged by sharp rocks. With a 4 to 24 minute one-way signal delay to Earth,
a rover cannot wait for a human to inspect every step.

## Scope

- **Mission phase:** surface operations (rover driving)
- **Target user:** rover drive planners on the ground, and the rover's onboard autonomy
- **What it does:** reads each navigation camera frame, labels every pixel as soil, bedrock, sand or big rock,
  scores the path directly ahead, and returns GO, CAUTION, STOP or HOLD with reasons
- **Data:** real Curiosity NAVCAM images with expert labels from NASA JPL's AI4Mars dataset
- **Not in scope:** steering or path planning, other rovers, orbital imagery, real hardware

## How it works

```
camera frame ──► quality checks ──► U-Net terrain map ──► path risk ──► GO / CAUTION / STOP / HOLD
                 (blur, exposure,    (soil, bedrock,       (sand, big rock,
                  corruption, loss)   sand, big rock)       uncertain pixels)
```

1. **Quality checks.** Lost, corrupted, blurry, dark or overexposed frames are rejected. The rover HOLDs
   instead of trusting a bad image.
2. **Terrain segmentation.** A U-Net CNN labels each pixel. Pixels where the model's confidence is low are
   marked *unknown* and treated as unsafe.
3. **Path risk.** The bottom-centre of the frame (the ground the rover is about to drive on) is scored by the
   share of sand, big rock and unknown terrain.
4. **Decision.** Risk thresholds give GO, CAUTION or STOP, with plain-language reasons such as
   "sand ahead (18% of path)".

## Data

[AI4Mars](https://data.nasa.gov/dataset/ai4mars-a-dataset-for-terrain-aware-autonomous-driving-on-mars)
(Swan et al., CVPR Workshops 2021), NASA JPL. Curiosity NAVCAM images, 1024 × 1024, with per-pixel labels:
soil, bedrock, sand, big rock, and unlabelled.

- **Train:** crowdsourced labels (at least 3 labellers, 2/3 agreement per pixel)
- **Test:** 322 images with expert labels and 100% agreement (`masked-gold-min3-100agree`)

Training uses the Kaggle mirror `yash92328/ai4mars-terrainaware-autonomous-driving-on-mars`.

## Evaluation

Both methods are scored on the expert-labelled test set, ignoring unlabelled pixels:

- **Baseline:** per-pixel logistic regression on brightness and local texture (no deep learning)
- **U-Net:** the CNN in `src/model.py`

Metrics: IoU per class, mean IoU and pixel accuracy. Sand IoU is the headline number.

| Method | Sand IoU | Big rock IoU | Mean IoU | Pixel accuracy |
|---|---|---|---|---|
| Baseline | – | – | – | – |
| U-Net | – | – | – | – |

*Filled in from `models/metrics.json` after training.*

## Getting started

### Install

```bash
git clone https://github.com/Kabir-88/Project-Ouranos.git
cd Project-Ouranos
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

### Train (on Kaggle, free GPU)

1. Upload `notebooks/train_kaggle.ipynb` to Kaggle.
2. Add the dataset `yash92328/ai4mars-terrainaware-autonomous-driving-on-mars` as input and turn on a GPU.
3. Run all cells. Download `terrain_unet.keras`, `metrics.json` and `demo_frames.zip` from the output.
4. Put `terrain_unet.keras` and `metrics.json` in `models/`, and unzip `demo_frames.zip` into `demo_frames/`.

### Run the dashboard

```bash
streamlit run app.py
```

The dashboard replays real test frames as a live rover camera feed. Use the sidebar to play the feed,
step through frames, compare with the expert label, and inject faults: blur, dark, overexposed,
corrupted pixels or a lost frame.

## Error handling

| Problem | Response |
|---|---|
| Frame lost in transmission | HOLD, counted as lost |
| Corrupted pixels | Frame rejected, HOLD |
| Blurry, too dark or overexposed | Frame rejected, HOLD |
| Model unsure about most of the frame | HOLD |
| Model unsure about some pixels | Marked unknown, counted as risk |
| Model or demo frames missing | Dashboard shows a clear setup message instead of crashing |

## Project structure

```
Project-Ouranos/
├── notebooks/
│   └── train_kaggle.ipynb  # data loading, U-Net training, baseline, evaluation, export
├── src/
│   ├── config.py           # classes, colours, thresholds
│   ├── model.py            # U-Net architecture
│   ├── inference.py        # frame quality checks, prediction, overlay
│   ├── traverse.py         # path risk score and GO / CAUTION / STOP / HOLD
│   └── stream.py           # replays frames as a live feed, fault injection
├── models/                 # terrain_unet.keras, metrics.json
├── demo_frames/            # expert-labelled test frames for the demo
├── app.py                  # Streamlit dashboard
└── requirements.txt
```

## Limitations

- Trained on Curiosity images only, so other rovers and cameras may perform worse.
- Labels describe terrain type, not soil strength. Sand is a proxy for "might get stuck".
- The path region is a fixed box ahead of the rover, not a planned route.
- Thresholds are set by hand, not tuned against real drive outcomes.

## Acknowledgements

- AI4Mars dataset: Swan, R. M., et al. (2021). *AI4MARS: A Dataset for Terrain-Aware Autonomous Driving on Mars.*
  CVPR Workshops. NASA JPL.
- Images: NASA/JPL-Caltech, Mars Science Laboratory (Curiosity).
