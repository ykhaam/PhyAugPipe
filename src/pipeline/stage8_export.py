from __future__ import annotations

import json
from pathlib import Path
import pandas as pd

from src.utils.jsonl import write_jsonl


def run(cfg: dict, scoring_cfg: dict, out_root: Path, rows_df: pd.DataFrame, logger) -> None:
    id_field = cfg["io"]["metadata_id_field"]
    split_field = cfg["io"]["metadata_split_field"]
    cap_field = cfg["io"]["metadata_caption_field"]

    by_id = {str(r[id_field]): r for r in rows_df.to_dict(orient="records")}
    merged = []
    for p in sorted((out_root / "parse_records").glob("*.json")):
        sid = p.stem
        parse = json.loads(p.read_text(encoding="utf-8"))
        prompt_p = out_root / "prompt_records" / f"{sid}.json"
        prompt = json.loads(prompt_p.read_text(encoding="utf-8")) if prompt_p.exists() else {}
        md = by_id.get(sid, {})
        merged.append({
            "sample_id": sid,
            "source_split": md.get(split_field),
            "source_metadata_reference": cfg["io"]["metadata_csv"],
            "local_video_path": md.get("local_video_path"),
            "original_caption": md.get(cap_field, ""),
            "cleaned_prompt": prompt.get("cleaned_prompt", ""),
            "extended_prompt": prompt.get("extended_prompt", ""),
            "parsed_entities": parse.get("vision_checked_parse", {}).get("entities", []),
            "parsed_actions": parse.get("vision_checked_parse", {}).get("actions", []),
            "parsed_forces": parse.get("vision_checked_parse", {}).get("forces", []),
            "parsed_outcomes": parse.get("vision_checked_parse", {}).get("outcomes", []),
            "physics_reasoning": parse.get("physics_reasoning", ""),
            "physics_richness": parse.get("physics_richness", 0.0),
            "physics_label": parse.get("physics_label", "low"),
            "penalty_breakdown": parse.get("penalties", {}),
            "shortlist_stage_tags": ["prefiltered"],
            "notes_for_later_construction": prompt.get("revision_notes", ""),
        })

    threshold = cfg["export"].get("threshold")
    if threshold is None:
        threshold = scoring_cfg["scoring"].get("export_threshold_default", 0.62)

    mode = cfg["export"].get("selection_mode", "threshold")
    if mode == "top_n":
        n = int(cfg["export"].get("top_n", 1000))
        winners = sorted(merged, key=lambda x: x["physics_richness"], reverse=True)[:n]
    else:
        winners = [m for m in merged if float(m["physics_richness"]) >= float(threshold)]

    win_ids = {w["sample_id"] for w in winners}
    rejected = [m for m in merged if m["sample_id"] not in win_ids]
    for m in winners:
        m["pass_fail"] = "pass"
    for m in rejected:
        m["pass_fail"] = "fail"

    exp = out_root / "final_exports"
    exp.mkdir(parents=True, exist_ok=True)
    write_jsonl(exp / "all_scored_samples.jsonl", merged)
    write_jsonl(exp / "passed_winners.jsonl", winners)
    write_jsonl(exp / "rejected_samples.jsonl", rejected)

    pd.DataFrame(merged).to_csv(exp / "all_scored_samples.csv", index=False)
    pd.DataFrame(winners).to_csv(exp / "passed_winners.csv", index=False)
    pd.DataFrame(rejected).to_csv(exp / "rejected_samples.csv", index=False)

    logger.info("passed threshold count=%s", len(winners))
    logger.info("rejected count=%s", len(rejected))
