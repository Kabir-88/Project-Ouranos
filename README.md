# Project Ouranos

**Catch spacecraft sensor anomalies before they become mission risks.**

Ouranos monitors spacecraft telemetry and flags abnormal sensor behaviour. For each telemetry channel, an LSTM network learns what normal looks like and predicts the next reading. When the actual reading drifts far from the prediction, Ouranos smooths the error and compares it to an adaptive threshold to decide whether it is an anomaly.

The model is trained and evaluated on real, labelled telemetry from NASA's **SMAP** satellite and the **Curiosity (MSL)** rover, and benchmarked against a rolling z-score baseline. A **Streamlit** dashboard replays each channel and shows predictions, errors and alerts as they happen.

---

## How it works

```
 telemetry ──► LSTM forecaster ──► prediction error ──► smoothing ──► adaptive threshold ──► alert
 (per channel)  (learns "normal")   |actual − predicted|   (EWMA)       (dynamic, per window)
```

1. **Forecast.** A separate LSTM is trained on each channel's nominal data. Given a window of recent readings (and command inputs), it predicts the next value.
2. **Measure error.** At every timestep, the absolute difference between the prediction and the actual reading is recorded.
3. **Smooth.** Raw errors are noisy, so they are smoothed with an exponentially weighted moving average. This stops one-off spikes from triggering alerts.
4. **Threshold.** Instead of a fixed cutoff, the threshold adapts to the recent error distribution. It is chosen to best separate unusually large errors from normal ones, so each channel gets a threshold that fits its own noise level.
5. **Flag.** Smoothed errors above the threshold are grouped into anomaly sequences. Small, isolated exceedances are pruned to cut down false positives.

## Dataset

Ouranos uses the public labelled telemetry dataset released by NASA JPL alongside [*Detecting Spacecraft Anomalies Using LSTMs and Nonparametric Dynamic Thresholding*](https://arxiv.org/abs/1802.04431) (Hundman et al., KDD 2018).

| Spacecraft | Channels | Description |
|---|---|---|
| SMAP (Soil Moisture Active Passive) | 55 | Earth-observing satellite |
| MSL (Mars Science Laboratory / Curiosity) | 27 | Mars rover |

Each channel has a train split (nominal behaviour) and a test split with expert-labelled anomaly windows. The data is anonymised: values are scaled and channel names are coded.

## Baseline

To show what the LSTM adds, every channel is also scored with a **rolling z-score** detector. It flags a point when it lies more than *k* standard deviations from the rolling mean of a trailing window. This is a simple, common method and gives a useful lower bound.

## Evaluation

Detection is scored per **anomaly event**, not per point:

- **True positive:** a predicted anomaly sequence overlaps a labelled anomaly window.
- **False positive:** a predicted sequence overlaps no labelled window.
- **False negative:** a labelled window with no overlapping prediction.

From these, Ouranos reports **precision**, **recall** and **F1** for each spacecraft and overall, for both the LSTM detector and the z-score baseline.

## Dashboard

The Streamlit dashboard replays a chosen channel's test data step by step and shows:

- actual telemetry alongside the LSTM's predictions
- the raw and smoothed prediction error
- the adaptive threshold as it changes
- detected anomalies, alongside the ground-truth labelled windows
- the same channel scored by the z-score baseline, for comparison

## Getting started

### Requirements

- Python 3.10+
- Dependencies in `requirements.txt` (TensorFlow/Keras or PyTorch, NumPy, pandas, scikit-learn, Streamlit, Plotly)

### Install

```bash
git clone https://github.com/Kabir-88/Project-Ouranos.git
cd Project-Ouranos
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Get the data

Download the SMAP/MSL dataset and labels from the [telemanom repository](https://github.com/khundman/telemanom):

```bash
curl -O https://s3-us-west-2.amazonaws.com/telemanom/data.zip
unzip data.zip && rm data.zip
curl -o data/labeled_anomalies.csv https://raw.githubusercontent.com/khundman/telemanom/master/labeled_anomalies.csv
```

This produces `data/train/`, `data/test/` and `data/labeled_anomalies.csv`.

### Run

```bash
# train a model for each channel and score the test set
python train.py

# score the rolling z-score baseline and compare
python evaluate.py

# launch the dashboard
streamlit run app.py
```

## Project structure

```
Project-Ouranos/
├── data/                  # SMAP/MSL telemetry and labels (not committed)
├── models/                # trained per-channel LSTM weights
├── ouranos/
│   ├── model.py           # LSTM forecaster
│   ├── errors.py          # error smoothing and adaptive thresholding
│   ├── baseline.py        # rolling z-score detector
│   └── metrics.py         # event-level precision / recall / F1
├── train.py
├── evaluate.py
├── app.py                 # Streamlit dashboard
└── requirements.txt
```

## Results

| Method | Precision | Recall | F1 |
|---|---|---|---|
| LSTM + adaptive threshold | – | – | – |
| Rolling z-score | – | – | – |

*Fill this in after running `evaluate.py`.*

## Acknowledgements

- Telemetry data and the original method: Hundman, K., Constantinou, V., Laporte, C., Colwell, I., & Soderstrom, T. (2018). *Detecting Spacecraft Anomalies Using LSTMs and Nonparametric Dynamic Thresholding.* KDD '18. [arXiv:1802.04431](https://arxiv.org/abs/1802.04431)
- NASA JPL, for releasing the SMAP and MSL labelled anomaly data.
