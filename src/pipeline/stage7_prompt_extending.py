from __future__ import annotations

import json

from src.storage.writers import write_sample_json
from src.vlm.prompt_templates import PROMPT_EXTEND_PROMPT


def run(cfg: dict, out_root, rows_df, vlm_runner, logger) -> None:
    cap_field = cfg["io"]["metadata_caption_field"]
    id_field = cfg["io"]["metadata_id_field"]
    by_id = {str(r[id_field]): r for r in rows_df.to_dict(orient="records")}
    processed = 0

    for p in sorted((out_root / "parse_records").glob("*.json")):
        parse_row = json.loads(p.read_text(encoding="utf-8"))
        sid = parse_row["sample_id"]
        out_path = out_root / "prompt_records" / f"{sid}.json"
        if out_path.exists() and not cfg["modes"].get("overwrite", False):
            continue
        md = by_id.get(sid, {})
        caption = md.get(cap_field, "")
        prompt = PROMPT_EXTEND_PROMPT.format(caption=caption, parse_json=json.dumps(parse_row.get("vision_checked_parse", {})), reasoning=parse_row.get("physics_reasoning", ""))
        obj = vlm_runner.infer_json(prompt, [])
        write_sample_json(out_root, "prompt_records", sid, {
            "sample_id": sid,
            "original_caption": caption,
            "cleaned_prompt": obj.get("cleaned_prompt", caption),
            "extended_prompt": obj.get("extended", obj.get("extended_prompt", caption)),
            "revision_notes": obj.get("notes", ""),
        }, overwrite=True)
        processed += 1

    logger.info("prompt extending processed samples=%s", processed)
