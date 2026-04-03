from __future__ import annotations


def apply_penalties(base_score: float, penalty_cfg: dict, flags: dict[str, bool]) -> tuple[float, dict[str, float]]:
    penalties = {}
    total = 0.0
    for k, amount in penalty_cfg.items():
        p = float(amount) if flags.get(k, False) else 0.0
        penalties[k] = p
        total += p
    return max(0.0, base_score - total), penalties
