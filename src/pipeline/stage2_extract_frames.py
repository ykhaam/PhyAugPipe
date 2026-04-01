from __future__ import annotations

from pathlib import Path
import pandas as pd

from src.video.video_locator import locate_video
from src.video.frame_cache import frame_cache_dir, has_cached_frames
from src.video.frame_sampler import sample_frames
from src.storage.writers import write_sample_json


def run(cfg: dict, out_root: Path, shortlist: pd.DataFrame, logger) -> pd.DataFrame:
    local_dirs = cfg["io"]["local_video_dirs"]
    frames_cfg = cfg["frames"]
    overwrite = cfg["modes"].get("overwrite", False)

    found = 0
    missing = 0
    rows = shortlist.to_dict(orient="records")
    for r in rows:
        sample_id = str(r[cfg["io"]["metadata_id_field"]])
        video_ref = str(r.get(cfg["io"]["metadata_video_ref_field"], ""))
        path = locate_video(video_ref, local_dirs) if video_ref else None
        r["local_video_path"] = path
        if path:
            found += 1
        else:
            missing += 1

        if not path or cfg["modes"].get("metadata_only", False):
            frame_paths = []
        else:
            fdir = frame_cache_dir(out_root, sample_id)
            if has_cached_frames(out_root, sample_id, 1) and not overwrite:
                frame_paths = [str(p) for p in sorted(fdir.glob("*.jpg"))]
            else:
                frame_paths = sample_frames(path, fdir, frames_cfg["strategy"], frames_cfg["num_frames"], frames_cfg["width"], frames_cfg["jpg_quality"])

        write_sample_json(out_root, "frame_records", sample_id, {
            "sample_id": sample_id,
            "local_video_path": path,
            "frame_paths": frame_paths,
            "sampling_strategy": frames_cfg["strategy"],
            "num_frames_requested": frames_cfg["num_frames"],
        }, overwrite=overwrite)

    logger.info("locally found videos=%s", found)
    logger.info("missing videos=%s", missing)
    return pd.DataFrame(rows)
