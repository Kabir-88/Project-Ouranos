"""Run the terrain model on one camera frame and check frame quality."""

import numpy as np
from PIL import Image

from src.config import (
    IMG_SIZE, CLASS_COLOURS, UNKNOWN_COLOUR, MIN_PIXEL_CONFIDENCE,
    MIN_SHARPNESS, MIN_BRIGHTNESS, MAX_BRIGHTNESS, MAX_UNKNOWN_FRACTION,
)


def preprocess(image):
    """PIL image or array -> float32 array (IMG_SIZE, IMG_SIZE) in [0, 1]."""
    if not isinstance(image, Image.Image):
        image = Image.fromarray(np.asarray(image))
    image = image.convert("L").resize((IMG_SIZE, IMG_SIZE), Image.BILINEAR)
    return np.asarray(image, dtype=np.float32) / 255.0


def sharpness(gray):
    """Variance of a Laplacian filter, scaled to 0-255 pixel units. Low means blurry."""
    g = gray * 255.0
    lap = (-4 * g[1:-1, 1:-1] + g[:-2, 1:-1] + g[2:, 1:-1] + g[1:-1, :-2] + g[1:-1, 2:])
    return float(lap.var())


def check_quality(gray):
    """Return a list of problems with the frame. Empty list means the frame is usable."""
    problems = []
    if not np.all(np.isfinite(gray)):
        problems.append("corrupted pixels")
        return problems
    brightness = float(gray.mean())
    if brightness < MIN_BRIGHTNESS:
        problems.append("too dark")
    if brightness > MAX_BRIGHTNESS:
        problems.append("overexposed")
    if sharpness(gray) < MIN_SHARPNESS:
        problems.append("blurry")
    return problems


def predict(model, gray):
    """Return (class map, confidence map). Low-confidence pixels get class -1 (unknown)."""
    probs = model.predict(gray[np.newaxis, :, :, np.newaxis], verbose=0)[0]
    classes = probs.argmax(axis=-1)
    confidence = probs.max(axis=-1)
    classes[confidence < MIN_PIXEL_CONFIDENCE] = -1
    return classes, confidence


def analyse_frame(model, image):
    """Full check for one frame. Returns a dict the dashboard can display."""
    raw = np.asarray(image, dtype=np.float32)
    if raw.size == 0 or not np.all(np.isfinite(raw)):
        blank = np.zeros((IMG_SIZE, IMG_SIZE), dtype=np.float32)
        return {"gray": blank, "classes": None, "confidence": None, "problems": ["corrupted pixels"]}

    gray = preprocess(image)
    problems = check_quality(gray)

    classes, confidence = predict(model, gray)
    unknown_fraction = float((classes == -1).mean())
    if unknown_fraction > MAX_UNKNOWN_FRACTION:
        problems.append("model unsure about most of the frame")
    return {"gray": gray, "classes": classes, "confidence": confidence, "problems": problems}


def overlay(gray, classes, alpha=0.45):
    """Colour the terrain classes on top of the grayscale frame. Returns uint8 RGB."""
    base = np.stack([gray * 255] * 3, axis=-1)
    colour = np.zeros_like(base)
    for c, rgb in enumerate(CLASS_COLOURS):
        colour[classes == c] = rgb
    colour[classes == -1] = UNKNOWN_COLOUR
    out = (1 - alpha) * base + alpha * colour
    return out.clip(0, 255).astype(np.uint8)
