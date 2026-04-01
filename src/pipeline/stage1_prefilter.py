from __future__ import annotations

from pathlib import Path
import pandas as pd

from src.metadata.panda70m_index import Panda70MIndex
from src.metadata.shortlist_builder import ShortlistBuilder
from src.utils.jsonl import write_jsonl


def run(cfg: dict, out_root: Path, logger) -> pd.DataFrame:
    idx = Panda70MIndex(cfg["io"]["metadata_csv"])
    df = idx.load()
    if cfg["modes"].get("smoke_test", False):
        df = idx.smoke_subset(df, cfg["modes"].get("smoke_test_n", 10))

    logger.info("total metadata entries=%s", len(df))

    s = cfg["shortlist"]
    sb = ShortlistBuilder(s["keywords"])
    short = sb.build(
        df,
        desirable_only=s["desirable_only"],
        single_shot_only=s["single_shot_only"],
        sports_dynamics_only=s["sports_dynamics_only"],
        duration_min_sec=s["duration_min_sec"],
        duration_max_sec=s["duration_max_sec"],
    )
    logger.info("shortlisted entries=%s", len(short))

    mdir = out_root / "metadata_records"
    mdir.mkdir(parents=True, exist_ok=True)
    short.to_csv(mdir / "shortlist.csv", index=False)
    write_jsonl(mdir / "shortlist.jsonl", short.to_dict(orient="records"))
    return short
