from __future__ import annotations

import json
import pandas as pd

from src.vlm.prompt_templates import PHYSICS_REASON_PROMPT


def run(cfg: dict, out_root, rows_df: pd.DataFrame, vlm_runner, logger) -> None:
    cap_field = cfg["io"]["metadata_caption_field"]
    id_field = cfg["io"]["metadata_id_field"]
    by_id = {str(r[id_field]): r for r in rows_df.to_dict(orient="records")}
    processed = 0
    for p in sorted((out_root / "parse_records").glob("*.json")):
        row = json.loads(p.read_text(encoding="utf-8"))
        if row.get("physics_reasoning") and not cfg["modes"].get("overwrite", False):
            continue
        sid = row.get("sample_id", p.stem)
        md = by_id.get(str(sid), {})
        frame_record_path = out_root / "frame_records" / f"{sid}.json"
        frame_paths: list[str] = []
        if frame_record_path.exists():
            frame_paths = json.loads(frame_record_path.read_text(encoding="utf-8")).get("frame_paths", [])

        prompt = PHYSICS_REASON_PROMPT.format(
            parse_json=json.dumps(row.get("vision_checked_parse", {})),
            caption=md.get("original_caption", md.get(cap_field, row.get("original", ""))),
            frame_hints=", ".join(frame_paths[:4]) if frame_paths else "[]",
        )
        resp = vlm_runner.infer_json(prompt, frame_paths)
        row["physics_reasoning"] = resp.get("reason", resp.get("text", "Visible cause-and-effect sequence."))
        p.write_text(json.dumps(row, ensure_ascii=False, indent=2), encoding="utf-8")
        processed += 1
    logger.info("physics reasoning processed samples=%s", processed)
