from __future__ import annotations


def physics_label(score: float, labels: dict) -> int:
    threshold = float(labels.get("positive", 0.60))
    return 1 if score >= threshold else 0
