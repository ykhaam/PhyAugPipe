from __future__ import annotations

from pathlib import Path
import json
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
        frame_record_path = out_root / "frame_records" / f"{sid}.json"
        frame_paths: list[str] = []
        if frame_record_path.exists():
            frame_paths = json.loads(frame_record_path.read_text(encoding="utf-8")).get("frame_paths", [])

        prompt = ELEMENT_PARSE_PROMPT.format(
            caption=r.get(cfg["io"]["metadata_caption_field"], ""),
            frame_hints=", ".join(frame_paths[:4]) if frame_paths else "[]",
        )
        obj = vlm_runner.infer_json(prompt, frame_paths)
        parse = normalize_parse(obj.get("parse", obj))
        write_sample_json(out_root, "parse_records", sid, {"sample_id": sid, "original": r.get(cfg["io"]["metadata_caption_field"], ""), "raw_parse": parse}, overwrite=True)
        processed += 1
    logger.info("element parsing processed samples=%s", processed)
