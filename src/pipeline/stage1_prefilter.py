from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Dict, List

import pandas as pd

from src.metadata.panda70m_index import Panda70MIndex, Panda70MIndexConfig
from src.metadata.shortlist_builder import ShortlistBuilder, ShortlistConfig
from src.storage.schemas import MetadataRecord
from src.storage.writers import write_sample_record
from src.utils.jsonl import write_jsonl


def run_stage1_prefilter(config: Dict, logger) -> List[MetadataRecord]:
    p70 = config["panda70m"]
    idx = Panda70MIndex(Panda70MIndexConfig(**p70["metadata"]))
    df = idx.load()

    if config["run"].get("smoke_test", False):
        df = df.head(int(config["run"].get("smoke_test_limit", 10)))

    logger.info("total metadata entries: %d", len(df))
    sb = ShortlistBuilder(p70["metadata"], ShortlistConfig(**p70["prefilter"]))
    shortlist = sb.build(df)
    logger.info("shortlisted entries: %d", len(shortlist))

    out_dir = Path(config["io"]["metadata_records_dir"])
    records: List[MetadataRecord] = []
    for _, row in shortlist.iterrows():
        rec = MetadataRecord(
            sample_id=str(row[p70["metadata"]["id_field"]]),
            split=str(row[p70["metadata"]["split_field"]]),
            source_metadata_ref=str(p70["metadata"]["input_csv"]),
            original_caption=str(row[p70["metadata"]["caption_field"]]),
            shortlist_tags=list(row["shortlist_tags"]),
            shortlist_pass=bool(row["shortlist_pass"]),
        )
        write_sample_record(out_dir, rec.sample_id, rec, overwrite=config["run"].get("overwrite", False))
        records.append(rec)

    write_jsonl(out_dir / "shortlist.jsonl", [r.to_dict() for r in records])
    pd.DataFrame([r.to_dict() for r in records]).to_csv(out_dir / "shortlist.csv", index=False)
    return records
