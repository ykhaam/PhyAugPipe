from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Dict


def _to_dict(record: Any) -> Dict[str, Any]:
    if is_dataclass(record):
        return asdict(record)
    if isinstance(record, dict):
        return record
    raise TypeError(f"Unsupported record type: {type(record)}")


def write_sample_record(root: str | Path, sample_id: str, record: Any, overwrite: bool = False) -> Path:
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    out_path = root / f"{sample_id}.json"
    if out_path.exists() and not overwrite:
        return out_path
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(_to_dict(record), f, ensure_ascii=False, indent=2)
    return out_path
