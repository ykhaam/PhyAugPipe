from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import pandas as pd

from src.scoring.thresholds import representative_bins
from src.storage.readers import iter_sample_records
from src.utils.jsonl import write_jsonl


def run_stage8_export(config, logger) -> None:
    meta_dir = Path(config["io"]["metadata_records_dir"])
    parse_dir = Path(config["io"]["parse_records_dir"])
    prompt_dir = Path(config["io"]["prompt_records_dir"])
    out_dir = Path(config["io"]["final_exports_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: List[Dict] = []
    for meta in iter_sample_records(meta_dir):
        sid = meta["sample_id"]
        pp = parse_dir / f"{sid}.json"
        if not pp.exists():
            continue
        prec = json.loads(pp.read_text())
        pr = {}
        prp = prompt_dir / f"{sid}.json"
        if prp.exists():
            pr = json.loads(prp.read_text())
        vc = prec.get("vision_checked_parse", {})
        rows.append({
            "sample_id": sid,
            "source_split": meta.get("split"),
            "source_metadata_reference": meta.get("source_metadata_ref"),
            "local_video_path": meta.get("local_video_path"),
            "original_caption": meta.get("original_caption"),
            "cleaned_prompt": pr.get("cleaned_prompt", ""),
            "extended_prompt": pr.get("extended_prompt", ""),
            "parsed_entities": vc.get("entities", []),
            "parsed_actions": vc.get("actions", []),
            "parsed_forces": vc.get("forces", []),
            "parsed_outcomes": vc.get("outcomes", []),
            "physics_reasoning": prec.get("physics_reasoning", ""),
            "physics_richness": prec.get("physics_richness", 0.0),
            "physics_label": prec.get("physics_label", "low"),
            "penalty_breakdown": prec.get("penalties", {}),
            "pass_fail_decision": prec.get("pass", False),
            "shortlist_stage_tags": meta.get("shortlist_tags", []),
            "notes_for_later_pairing": "winner candidate from physics-richness pipeline",
        })

    df = pd.DataFrame(rows)
    if df.empty:
        logger.warning("No rows to export.")
        return

    scores = df["physics_richness"].astype(float).tolist()
    bins = representative_bins(scores, config["scoring"]["score_binning"]["bins"])
    with (out_dir / "score_distribution.json").open("w", encoding="utf-8") as f:
        json.dump(bins, f, indent=2)

    selection_cfg = config["scoring"]["selection"]
    if selection_cfg.get("mode") == "top_n":
        passed = df.sort_values("physics_richness", ascending=False).head(int(selection_cfg.get("top_n", 1000)))
    else:
        passed = df[df["pass_fail_decision"] == True]

    rejected = df[df["pass_fail_decision"] == False]

    df.to_csv(out_dir / "all_scored_samples.csv", index=False)
    passed.to_csv(out_dir / "passed_winners.csv", index=False)
    rejected.to_csv(out_dir / "rejected_samples.csv", index=False)

    write_jsonl(out_dir / "all_scored_samples.jsonl", df.to_dict(orient="records"))
    write_jsonl(out_dir / "passed_winners.jsonl", passed.to_dict(orient="records"))
    write_jsonl(out_dir / "rejected_samples.jsonl", rejected.to_dict(orient="records"))

    logger.info("passed threshold count: %d", len(passed))
    logger.info("rejected count: %d", len(rejected))
