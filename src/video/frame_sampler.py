from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import cv2

from src.video.frame_cache import frame_cache_dir


def _pick_indices(frame_count: int, num_frames: int, strategy: str, middle_only: bool) -> List[int]:
    if frame_count <= 0:
        return []
    if middle_only or strategy == "middle":
        return [frame_count // 2]
    if num_frames <= 1:
        return [0]
    step = max(frame_count // num_frames, 1)
    idx = list(range(0, frame_count, step))[:num_frames]
    if not idx:
        idx = [0]
    return idx


def sample_frames(
    video_path: str,
    out_root: str,
    sample_id: str,
    strategy: str = "uniform",
    num_frames: int = 8,
    middle_only: bool = False,
) -> Dict:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {
            "sample_id": sample_id,
            "frame_paths": [],
            "sampling_strategy": strategy,
            "num_frames_requested": num_frames,
            "num_frames_extracted": 0,
            "metadata": {"error": "failed_to_open_video"},
        }

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    indices = _pick_indices(total, num_frames, strategy, middle_only)

    out_dir = frame_cache_dir(out_root, sample_id)
    frame_paths: List[str] = []

    for i, idx in enumerate(indices):
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, frame = cap.read()
        if not ok:
            continue
        path = out_dir / f"frame_{i:03d}.jpg"
        cv2.imwrite(str(path), frame)
        frame_paths.append(str(path))

    cap.release()
    return {
        "sample_id": sample_id,
        "frame_paths": frame_paths,
        "sampling_strategy": "middle" if middle_only else strategy,
        "num_frames_requested": 1 if middle_only else num_frames,
        "num_frames_extracted": len(frame_paths),
        "metadata": {"total_frames": total, "fps": fps, "indices": indices},
    }
