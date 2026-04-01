from __future__ import annotations

from typing import Dict, List


def physics_label(score: float) -> str:
    if score >= 0.8:
        return "high"
    if score >= 0.55:
        return "medium"
    return "low"


def decide_pass(score: float, selection_cfg: Dict) -> bool:
    mode = selection_cfg.get("mode", "threshold")
    if mode == "threshold":
        return score >= float(selection_cfg.get("threshold", 0.55))
    return True


def representative_bins(scores: List[float], bins: List[float]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for s in scores:
        for i in range(len(bins) - 1):
            lo, hi = bins[i], bins[i + 1]
            if lo <= s < hi or (i == len(bins) - 2 and s == hi):
                key = f"[{lo:.2f},{hi:.2f}]"
                counts[key] = counts.get(key, 0) + 1
                break
    return counts
