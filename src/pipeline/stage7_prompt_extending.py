from __future__ import annotations

import json
from pathlib import Path

from src.utils.distributed import shard_items
from src.storage.readers import iter_sample_records
from src.storage.writers import write_sample_record


def run_stage7_prompt_extending(config, logger, runner) -> None:
    parse_dir = Path(config["io"]["parse_records_dir"])
    meta_dir = Path(config["io"]["metadata_records_dir"])
    prompt_dir = Path(config["io"]["prompt_records_dir"])

    meta_records = list(iter_sample_records(meta_dir))
    shard_records = shard_items(meta_records, config["execution"]["num_shards"], config["execution"]["shard_id"])
    logger.info("stage7 shard samples: %d / %d", len(shard_records), len(meta_records))
    for meta in shard_records:
        sid = meta["sample_id"]
        pp = parse_dir / f"{sid}.json"
        if not pp.exists():
            continue
        if (prompt_dir / f"{sid}.json").exists() and not config["run"].get("overwrite", False):
            continue
        prec = json.loads(pp.read_text())
        ext = runner.extend_prompt(meta["original_caption"], prec.get("vision_checked_parse", {}), prec.get("physics_reasoning", ""))
        out = {
            "sample_id": sid,
            "original_caption": meta["original_caption"],
            "cleaned_prompt": ext["cleaned_prompt"],
            "extended_prompt": ext["extended_prompt"],
            "revision_notes": ["frame-grounded", "non-hallucinatory"],
        }
        write_sample_record(prompt_dir, sid, out, overwrite=True)
