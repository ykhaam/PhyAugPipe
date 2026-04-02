import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse
import subprocess

import pandas as pd


def hms_to_sec(v: str) -> float:
    h, m, s = v.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def run_cmd(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def ensure_video_download(url: str, video_id: str, raw_dir: Path) -> Path:
    raw_dir.mkdir(parents=True, exist_ok=True)
    out_file = raw_dir / f"{video_id}.mp4"
    if out_file.exists() and out_file.stat().st_size > 0:
        return out_file

    # yt-dlp writes to exact file name template.
    run_cmd([
        "yt-dlp",
        "-f",
        "mp4",
        "-o",
        str(out_file),
        url,
    ])
    return out_file


def ensure_clip(raw_video: Path, clip_out: Path, start: str, end: str) -> None:
    if clip_out.exists() and clip_out.stat().st_size > 0:
        return

    clip_out.parent.mkdir(parents=True, exist_ok=True)
    duration = max(0.1, hms_to_sec(end) - hms_to_sec(start))
    run_cmd([
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-ss",
        start,
        "-i",
        str(raw_video),
        "-t",
        f"{duration:.3f}",
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        str(clip_out),
    ])


def main() -> None:
    ap = argparse.ArgumentParser(description="Download Panda subset videos/clips with resume behavior")
    ap.add_argument("--input-csv", required=True, help="Filtered CSV (e.g., train_2m_sports_30k.csv)")
    ap.add_argument("--raw-video-dir", default="data/videos_raw")
    ap.add_argument("--clip-dir", default="data/videos")
    ap.add_argument("--max-downloads", type=int, default=0, help="0 means all")
    args = ap.parse_args()

    df = pd.read_csv(args.input_csv)
    required = {"sample_id", "videoID", "url", "clip_start", "clip_end"}
    missing_cols = sorted(required - set(df.columns))
    if missing_cols:
        raise ValueError(f"missing required columns: {missing_cols}")

    raw_dir = Path(args.raw_video_dir)
    clip_dir = Path(args.clip_dir)

    done = 0
    skipped = 0
    errors = 0

    for _, row in df.iterrows():
        if args.max_downloads > 0 and done >= args.max_downloads:
            break

        sample_id = str(row["sample_id"])
        video_id = str(row["videoID"])
        url = str(row["url"])
        clip_start = str(row["clip_start"])
        clip_end = str(row["clip_end"])

        clip_out = clip_dir / f"{sample_id}.mp4"
        if clip_out.exists() and clip_out.stat().st_size > 0:
            skipped += 1
            continue

        try:
            raw_video = ensure_video_download(url, video_id, raw_dir)
            ensure_clip(raw_video, clip_out, clip_start, clip_end)
            done += 1
        except subprocess.CalledProcessError:
            errors += 1

    print({
        "requested_rows": len(df) if args.max_downloads == 0 else min(len(df), args.max_downloads),
        "downloaded_or_clipped": done,
        "skipped_existing": skipped,
        "errors": errors,
        "clip_dir": str(clip_dir),
        "raw_video_dir": str(raw_dir),
    })


if __name__ == "__main__":
    main()
