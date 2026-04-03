from __future__ import annotations

from pathlib import Path


def frame_cache_dir(root: Path, sample_id: str) -> Path:
    p = root / "frame_records" / sample_id
    p.mkdir(parents=True, exist_ok=True)
    return p


def has_cached_frames(root: Path, sample_id: str, min_count: int) -> bool:
    p = root / "frame_records" / sample_id
    if not p.exists():
        return False
    return len(list(p.glob("*.jpg"))) >= min_count
