from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from src.storage.readers import iter_sample_records, has_sample_record
from src.storage.schemas import FrameRecord
from src.storage.writers import write_sample_record
from src.video.frame_cache import has_cached_frames
from src.video.frame_sampler import sample_frames
from src.video.video_locator import find_local_video


def run_stage2_extract_frames(config: Dict, logger) -> None:
    p70 = config["panda70m"]
    meta_dir = Path(config["io"]["metadata_records_dir"])
    frame_dir = Path(config["io"]["frame_records_dir"])

    found = 0
    missing = 0
    processed = 0

    for rec in iter_sample_records(meta_dir):
        sample_id = rec["sample_id"]
        if has_sample_record(frame_dir, sample_id) and not config["run"].get("overwrite", False):
            continue

        local = find_local_video(
            rec.get("sample_id", ""),
            p70["videos"]["local_video_roots"],
            p70["videos"]["allowed_exts"],
        )
        rec["local_video_path"] = local
        rec["local_video_found"] = bool(local)
        write_sample_record(meta_dir, sample_id, rec, overwrite=True)

        if not local:
            missing += 1
            logger.info("missing local video: %s", sample_id)
            continue

        found += 1
        if has_cached_frames(str(frame_dir), sample_id) and not config["run"].get("overwrite", False):
            continue

        fr = sample_frames(
            local,
            str(frame_dir),
            sample_id,
            strategy=p70["frames"].get("sampling_strategy", "uniform"),
            num_frames=int(p70["frames"].get("num_frames", 8)),
            middle_only=bool(p70["frames"].get("middle_frame_only", False)),
        )
        write_sample_record(frame_dir, sample_id, FrameRecord(**fr), overwrite=True)
        processed += 1

    logger.info("locally found videos: %d", found)
    logger.info("missing videos: %d", missing)
    logger.info("processed samples: %d", processed)
