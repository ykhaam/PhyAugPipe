from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional


def find_local_video(video_ref: str, roots: Iterable[str], allowed_exts: Iterable[str]) -> Optional[str]:
    ref = Path(video_ref)
    exts = {e.lower() for e in allowed_exts}

    candidates = []
    if ref.suffix.lower() in exts:
        candidates.append(ref.name)
    else:
        for ext in exts:
            candidates.append(ref.name + ext)
            candidates.append(ref.stem + ext)

    for r in roots:
        base = Path(r)
        for c in candidates:
            p = base / c
            if p.exists():
                return str(p.resolve())
    return None
