from __future__ import annotations

from pathlib import Path
from typing import Dict

from src.utils.distributed import shard_items
from src.storage.readers import iter_sample_records, has_sample_record
from src.storage.writers import write_sample_record
from src.vlm.parser import ensure_parse_schema


def run_stage3_element_parsing(config: Dict, logger, runner) -> None:
    meta_dir = Path(config["io"]["metadata_records_dir"])
    frame_dir = Path(config["io"]["frame_records_dir"])
    parse_dir = Path(config["io"]["parse_records_dir"])

    meta_records = list(iter_sample_records(meta_dir))
    shard_records = shard_items(meta_records, config["execution"]["num_shards"], config["execution"]["shard_id"])
    logger.info("stage3 shard samples: %d / %d", len(shard_records), len(meta_records))
    for meta in shard_records:
        sid = meta["sample_id"]
        if has_sample_record(parse_dir, sid) and not config["run"].get("overwrite", False):
            continue
        frame_rec = (frame_dir / f"{sid}.json")
        frame_paths = []
        if frame_rec.exists():
            import json
            frame_paths = json.loads(frame_rec.read_text()).get("frame_paths", [])
        raw = ensure_parse_schema(runner.element_parse(meta["original_caption"], frame_paths))
        write_sample_record(parse_dir, sid, {"sample_id": sid, "raw_parse": raw}, overwrite=True)
