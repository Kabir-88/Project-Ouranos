"""Decide whether the path ahead of the rover is safe to drive."""

import numpy as np

from src.config import CLASS_NAMES, HAZARD_WEIGHTS, CAUTION_RISK, STOP_RISK


def path_region(shape, width_frac=0.4, height_frac=0.5):
    """Boolean mask for the area straight ahead: bottom-centre of the frame (closest to the rover)."""
    h, w = shape
    mask = np.zeros(shape, dtype=bool)
    left = int(w * (1 - width_frac) / 2)
    right = int(w * (1 + width_frac) / 2)
    top = int(h * (1 - height_frac))
    mask[top:, left:right] = True
    return mask


def assess_path(classes):
    """Return a dict with class fractions in the path, a risk score, a decision and the reasons."""
    region = classes[path_region(classes.shape)]
    total = region.size

    fractions = {}
    for c, name in enumerate(CLASS_NAMES):
        fractions[name] = float((region == c).sum()) / total
    fractions["unknown"] = float((region == -1).sum()) / total

    risk = 0.0
    for name, weight in HAZARD_WEIGHTS.items():
        risk += weight * fractions[name]
    risk = min(risk, 1.0)

    reasons = []
    if fractions["sand"] > 0.05:
        reasons.append("sand ahead (" + str(round(fractions["sand"] * 100)) + "% of path)")
    if fractions["big rock"] > 0.05:
        reasons.append("big rocks ahead (" + str(round(fractions["big rock"] * 100)) + "% of path)")
    if fractions["unknown"] > 0.10:
        reasons.append("uncertain terrain (" + str(round(fractions["unknown"] * 100)) + "% of path)")

    if risk >= STOP_RISK:
        decision = "STOP"
    elif risk >= CAUTION_RISK:
        decision = "CAUTION"
    else:
        decision = "GO"
    return {"fractions": fractions, "risk": risk, "decision": decision, "reasons": reasons}


def blocked_decision(problems):
    """Decision when the frame itself can't be trusted. Unknown terrain is treated as unsafe."""
    return {"fractions": {}, "risk": 1.0, "decision": "HOLD", "reasons": ["bad frame: " + ", ".join(problems)]}
