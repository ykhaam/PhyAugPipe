from __future__ import annotations

from pathlib import Path
from typing import Iterable


def locate_video(video_ref: str, local_dirs: Iterable[str]) -> str | None:
    ref_name = Path(str(video_ref)).name
    for d in local_dirs:
        direct = Path(d) / ref_name
        if direct.exists():
            return str(direct)
    return None
