from __future__ import annotations

import json
from pathlib import Path

from src.vlm.prompt_templates import VISION_CHECK_PROMPT
from src.vlm.parser import normalize_parse


def run(cfg: dict, out_root: Path, vlm_runner, logger) -> None:
    processed = 0
    for p in sorted((out_root / "parse_records").glob("*.json")):
        row = json.loads(p.read_text(encoding="utf-8"))
        if row.get("vision_checked_parse") and not cfg["modes"].get("overwrite", False):
            continue
        prompt = VISION_CHECK_PROMPT.format(parse_json=json.dumps(row.get("raw_parse", {})), caption="")
        row["vision_checked_parse"] = normalize_parse(vlm_runner.infer_json(prompt, []))
        p.write_text(json.dumps(row, ensure_ascii=False, indent=2), encoding="utf-8")
        processed += 1
    logger.info("vision checking processed samples=%s", processed)
