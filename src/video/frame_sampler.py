from __future__ import annotations

from pathlib import Path
import cv2


def sample_frames(video_path: str, out_dir: Path, strategy: str, num_frames: int, width: int, jpg_quality: int) -> list[str]:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total <= 0:
        cap.release()
        return []

    if strategy == "middle":
        idxs = [total // 2]
    else:
        step = max(total // max(num_frames, 1), 1)
        idxs = [min(i * step, total - 1) for i in range(num_frames)]

    paths: list[str] = []
    for n, idx in enumerate(idxs):
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, frame = cap.read()
        if not ok:
            continue
        h, w = frame.shape[:2]
        if w > width:
            new_h = int(h * width / w)
            frame = cv2.resize(frame, (width, new_h))
        out_path = out_dir / f"frame_{n:03d}.jpg"
        cv2.imwrite(str(out_path), frame, [int(cv2.IMWRITE_JPEG_QUALITY), int(jpg_quality)])
        paths.append(str(out_path))

    cap.release()
    return paths
