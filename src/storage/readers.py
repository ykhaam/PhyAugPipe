from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterator


def iter_sample_records(root: str | Path) -> Iterator[Dict]:
    root = Path(root)
    if not root.exists():
        return iter(())
    for p in sorted(root.glob("*.json")):
        with p.open("r", encoding="utf-8") as f:
            yield json.load(f)


def has_sample_record(root: str | Path, sample_id: str) -> bool:
    return (Path(root) / f"{sample_id}.json").exists()
