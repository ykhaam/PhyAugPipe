from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_sample_json(root: Path, stage: str, sample_id: str, payload: dict[str, Any], overwrite: bool = False) -> Path:
    out_dir = root / stage
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{sample_id}.json"
    if out_path.exists() and not overwrite:
        return out_path
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path
