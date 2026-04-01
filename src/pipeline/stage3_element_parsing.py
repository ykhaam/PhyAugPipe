from __future__ import annotations

from pathlib import Path
import pandas as pd

from src.storage.writers import write_sample_json
from src.vlm.prompt_templates import ELEMENT_PARSE_PROMPT
from src.vlm.parser import normalize_parse


def run(cfg: dict, out_root: Path, rows: pd.DataFrame, vlm_runner, logger) -> None:
    overwrite = cfg["modes"].get("overwrite", False)
    processed = 0
    for r in rows.to_dict(orient="records"):
        sid = str(r[cfg["io"]["metadata_id_field"]])
        out_path = out_root / "parse_records" / f"{sid}.json"
        if out_path.exists() and not overwrite:
            continue
        prompt = ELEMENT_PARSE_PROMPT.format(caption=r.get(cfg["io"]["metadata_caption_field"], ""))
        parse = normalize_parse(vlm_runner.infer_json(prompt, []))
        write_sample_json(out_root, "parse_records", sid, {"sample_id": sid, "raw_parse": parse}, overwrite=True)
        processed += 1
    logger.info("element parsing processed samples=%s", processed)
