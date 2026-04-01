from __future__ import annotations

import json

from src.vlm.prompt_templates import PHYSICS_REASON_PROMPT


def run(cfg: dict, out_root, vlm_runner, logger) -> None:
    processed = 0
    for p in sorted((out_root / "parse_records").glob("*.json")):
        row = json.loads(p.read_text(encoding="utf-8"))
        if row.get("physics_reasoning") and not cfg["modes"].get("overwrite", False):
            continue
        prompt = PHYSICS_REASON_PROMPT.format(parse_json=json.dumps(row.get("vision_checked_parse", {})), caption="")
        resp = vlm_runner.infer_json(prompt, [])
        row["physics_reasoning"] = resp.get("text", "Visible cause-and-effect sequence.")
        p.write_text(json.dumps(row, ensure_ascii=False, indent=2), encoding="utf-8")
        processed += 1
    logger.info("physics reasoning processed samples=%s", processed)
