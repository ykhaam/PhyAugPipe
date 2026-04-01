from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from src.utils.distributed import shard_items
from src.storage.readers import iter_sample_records
from src.storage.writers import write_sample_record


def run_stage4_vision_checking(config: Dict, logger, runner) -> None:
    parse_dir = Path(config["io"]["parse_records_dir"])
    meta_dir = Path(config["io"]["metadata_records_dir"])
    frame_dir = Path(config["io"]["frame_records_dir"])

    meta_records = list(iter_sample_records(meta_dir))
    shard_records = shard_items(meta_records, config["execution"]["num_shards"], config["execution"]["shard_id"])
    logger.info("stage4 shard samples: %d / %d", len(shard_records), len(meta_records))
    for meta in shard_records:
        sid = meta["sample_id"]
        pp = parse_dir / f"{sid}.json"
        if not pp.exists():
            continue
        rec = json.loads(pp.read_text())
        if "vision_checked_parse" in rec and not config["run"].get("overwrite", False):
            continue
        frame_paths = []
        fp = frame_dir / f"{sid}.json"
        if fp.exists():
            frame_paths = json.loads(fp.read_text()).get("frame_paths", [])
        checked = runner.vision_check(rec.get("raw_parse", {}), meta["original_caption"], frame_paths)
        rec["vision_checked_parse"] = checked
        write_sample_record(parse_dir, sid, rec, overwrite=True)
