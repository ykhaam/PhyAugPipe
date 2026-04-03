from __future__ import annotations

from pathlib import Path
import pandas as pd

from src.metadata.panda70m_index import Panda70MIndex
from src.metadata.prompt_fields import attach_original_caption_column
from src.metadata.shortlist_builder import ShortlistBuilder
from src.utils.jsonl import write_jsonl


def run(cfg: dict, out_root: Path, logger) -> pd.DataFrame:
    idx = Panda70MIndex(cfg["io"]["metadata_csv"])
    df = idx.load()
    df, prompt_field = attach_original_caption_column(df, cfg["io"].get("metadata_caption_field"))
    empty_prompt_rows = int((df["original_caption"].str.strip() == "").sum())
    if empty_prompt_rows > 0:
        logger.warning("rows with empty original_caption=%s", empty_prompt_rows)
    if cfg["modes"].get("smoke_test", False):
        df = idx.smoke_subset(df, cfg["modes"].get("smoke_test_n", 10))

    logger.info("total metadata entries=%s", len(df))
    logger.info("resolved prompt field=%s", prompt_field)

    s = cfg["shortlist"]
    sb = ShortlistBuilder(s["keywords"])
    short = sb.build(
        df,
        desirable_only=s["desirable_only"],
        single_shot_only=s["single_shot_only"],
        sports_dynamics_only=s["sports_dynamics_only"],
        duration_min_sec=s["duration_min_sec"],
        duration_max_sec=s["duration_max_sec"],
        random_shuffle=s.get("random_shuffle", False),
        random_seed=int(s.get("random_seed", 42)),
        max_samples=s.get("max_samples"),
    )
    logger.info("shortlisted entries=%s", len(short))

    mdir = out_root / "metadata_records"
    mdir.mkdir(parents=True, exist_ok=True)
    short.to_csv(mdir / "shortlist.csv", index=False)
    write_jsonl(mdir / "shortlist.jsonl", short.to_dict(orient="records"))
    return short
