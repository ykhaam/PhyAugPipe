from __future__ import annotations


def physics_label(score: float, labels: dict) -> str:
    if score >= labels.get("high", 0.75):
        return "high"
    if score >= labels.get("medium", 0.5):
        return "medium"
    return "low"
