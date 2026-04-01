from __future__ import annotations

from typing import Dict


def estimate_penalties(metadata: Dict, parse_checked: Dict, penalty_cfg: Dict[str, float]) -> Dict[str, float]:
    caption = str(metadata.get("original_caption", "")).lower()
    penalties = {
        "heavy_camera_motion": penalty_cfg.get("heavy_camera_motion", 0.0)
        if any(k in caption for k in ["shaky", "camera pans fast", "blurred"])
        else 0.0,
        "stylized_non_natural_visuals": penalty_cfg.get("stylized_non_natural_visuals", 0.0)
        if any(k in caption for k in ["cartoon", "animation", "cgi", "render"])
        else 0.0,
        "static_aftermath_weak_dynamic_event": penalty_cfg.get("static_aftermath_weak_dynamic_event", 0.0)
        if len(parse_checked.get("actions", [])) == 0
        else 0.0,
    }
    return penalties


def apply_penalties(score: float, penalties: Dict[str, float]) -> float:
    return max(0.0, score - sum(penalties.values()))
