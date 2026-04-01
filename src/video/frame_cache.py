from __future__ import annotations

from pathlib import Path


def frame_cache_dir(root: str, sample_id: str) -> Path:
    p = Path(root) / sample_id
    p.mkdir(parents=True, exist_ok=True)
    return p


def has_cached_frames(root: str, sample_id: str) -> bool:
    p = Path(root) / sample_id
    return p.exists() and any(p.glob("*.jpg"))
