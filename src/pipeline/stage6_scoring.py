from __future__ import annotations

import json

from src.scoring.richness import compute_richness
from src.scoring.penalties import apply_penalties
from src.scoring.thresholds import physics_label


def run(cfg: dict, scoring_cfg: dict, out_root, logger) -> None:
    processed = 0
    comp_w = scoring_cfg["scoring"]["components"]
    p_cfg = scoring_cfg["scoring"]["penalties"]
    labels = scoring_cfg["scoring"]["labels"]

    for p in sorted((out_root / "parse_records").glob("*.json")):
        row = json.loads(p.read_text(encoding="utf-8"))
        if row.get("physics_richness") is not None and not cfg["modes"].get("overwrite", False):
            continue

        parse = row.get("vision_checked_parse") or row.get("raw_parse", {})
        reason = str(row.get("physics_reasoning", "")).strip()
        causal_clarity = min(max(len(reason.split()) / 20.0, 0.2), 1.0)
        base, comps = compute_richness(
            len(parse.get("entities", [])),
            len(parse.get("actions", [])),
            len(parse.get("forces", [])),
            len(parse.get("outcomes", [])),
            causal_clarity=causal_clarity,
            weights=comp_w,
        )
        flags = {
            "heavy_camera_motion": False,
            "stylization_non_natural": False,
            "static_aftermath_weak_event": False,
        }
        score, penalties = apply_penalties(base, p_cfg, flags)
        row["score_components"] = comps
        row["penalties"] = penalties
        row["physics_richness"] = round(score, 4)
        row["physics_label"] = physics_label(score, labels)
        p.write_text(json.dumps(row, ensure_ascii=False, indent=2), encoding="utf-8")
        processed += 1
    logger.info("scoring processed samples=%s", processed)
