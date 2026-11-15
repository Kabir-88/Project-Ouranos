"""Shared settings for Project Ouranos."""

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(ROOT, "models", "terrain_unet.keras")
METRICS_PATH = os.path.join(ROOT, "models", "metrics.json")
FRAMES_DIR = os.path.join(ROOT, "demo_frames")

# Model input size (AI4Mars images are 1024x1024, we downsample)
IMG_SIZE = 256

# AI4Mars terrain classes (label value -> name). 255 means unlabelled.
CLASS_NAMES = ["soil", "bedrock", "sand", "big rock"]
NUM_CLASSES = 4
NULL_LABEL = 255

# Overlay colours (RGB) for each class
CLASS_COLOURS = [
    (194, 154, 108),  # soil: tan
    (120, 120, 120),  # bedrock: grey
    (240, 200, 40),   # sand: yellow
    (220, 50, 50),    # big rock: red
]
UNKNOWN_COLOUR = (60, 60, 200)  # low confidence: blue

# Hazard classes and how much each one adds to path risk
HAZARD_WEIGHTS = {"sand": 1.0, "big rock": 1.0, "unknown": 0.5}

# Decision thresholds on the risk score of the path ahead (0 to 1)
CAUTION_RISK = 0.10
STOP_RISK = 0.25

# A pixel is "unknown" if the model's top class probability is below this
MIN_PIXEL_CONFIDENCE = 0.6

# Frame quality checks
MIN_SHARPNESS = 20.0      # variance of Laplacian; lower means blurry
MIN_BRIGHTNESS = 0.08     # mean pixel value in [0, 1]
MAX_BRIGHTNESS = 0.92
MAX_UNKNOWN_FRACTION = 0.5
