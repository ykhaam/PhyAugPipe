from __future__ import annotations

import json
from pathlib import Path

from src.scoring.penalties import apply_penalties, estimate_penalties
from src.scoring.richness import aggregate_score, component_scores
from src.scoring.thresholds import physics_label, decide_pass
from src.utils.distributed import shard_items
from src.storage.readers import iter_sample_records
from src.storage.writers import write_sample_record


def run_stage6_scoring(config, logger) -> None:
    parse_dir = Path(config["io"]["parse_records_dir"])
    meta_dir = Path(config["io"]["metadata_records_dir"])
    scfg = config["scoring"]

    meta_records = list(iter_sample_records(meta_dir))
    shard_records = shard_items(meta_records, config["execution"]["num_shards"], config["execution"]["shard_id"])
    logger.info("stage6 shard samples: %d / %d", len(shard_records), len(meta_records))
    for meta in shard_records:
        sid = meta["sample_id"]
        pp = parse_dir / f"{sid}.json"
        if not pp.exists():
            continue
        rec = json.loads(pp.read_text())
        if rec.get("physics_richness") is not None and not config["run"].get("overwrite", False):
            continue
        comps = component_scores(rec.get("vision_checked_parse", {}), rec.get("physics_reasoning", ""))
        raw = aggregate_score(comps, scfg["weights"])
        pens = estimate_penalties(meta, rec.get("vision_checked_parse", {}), scfg["penalties"])
        final = apply_penalties(raw, pens)
        rec["score_components"] = comps
        rec["penalties"] = pens
        rec["physics_richness"] = final
        rec["physics_label"] = physics_label(final)
        rec["pass"] = decide_pass(final, scfg["selection"])
        write_sample_record(parse_dir, sid, rec, overwrite=True)
