import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse
import json
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


def save_prompt_sidecar(
    sample_id: str,
    caption: str,
    prompt_dir: Path | None,
    metadata_dir: Path | None,
    row_payload: dict[str, str],
) -> None:
    if prompt_dir is not None:
        prompt_dir.mkdir(parents=True, exist_ok=True)
        (prompt_dir / f"{sample_id}.txt").write_text(caption, encoding="utf-8")

    if metadata_dir is not None:
        metadata_dir.mkdir(parents=True, exist_ok=True)
        (metadata_dir / f"{sample_id}.json").write_text(
            json.dumps(row_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def main() -> None:
    ap = argparse.ArgumentParser(description="Download Panda subset videos/clips with resume behavior")
    ap.add_argument("--input-csv", required=True, help="Filtered CSV (e.g., train_2m_sports_30k.csv)")
    ap.add_argument("--raw-video-dir", default="data/videos_raw")
    ap.add_argument("--clip-dir", default="data/videos")
    ap.add_argument("--save-prompts-dir", default="", help="Optional: write <sample_id>.txt captions")
    ap.add_argument("--save-metadata-dir", default="", help="Optional: write <sample_id>.json row metadata")
    ap.add_argument("--max-downloads", type=int, default=0, help="0 means all")
    args = ap.parse_args()

    df = pd.read_csv(args.input_csv)
    required = {"sample_id", "videoID", "url", "clip_start", "clip_end"}
    missing_cols = sorted(required - set(df.columns))
    if missing_cols:
        raise ValueError(f"missing required columns: {missing_cols}")

    raw_dir = Path(args.raw_video_dir)
    clip_dir = Path(args.clip_dir)
    prompts_dir = Path(args.save_prompts_dir) if args.save_prompts_dir else None
    metadata_dir = Path(args.save_metadata_dir) if args.save_metadata_dir else None

    done = 0
    skipped = 0
    errors = 0
    prompt_saved = 0

    for _, row in df.iterrows():
        if args.max_downloads > 0 and done >= args.max_downloads:
            break

        sample_id = str(row["sample_id"])
        video_id = str(row["videoID"])
        url = str(row["url"])
        clip_start = str(row["clip_start"])
        clip_end = str(row["clip_end"])
        caption = str(row.get("caption", ""))
        row_payload = {k: str(v) for k, v in row.to_dict().items()}

        clip_out = clip_dir / f"{sample_id}.mp4"
        if clip_out.exists() and clip_out.stat().st_size > 0:
            skipped += 1
            if prompts_dir is not None or metadata_dir is not None:
                save_prompt_sidecar(sample_id, caption, prompts_dir, metadata_dir, row_payload)
                prompt_saved += 1
            continue

        try:
            raw_video = ensure_video_download(url, video_id, raw_dir)
            ensure_clip(raw_video, clip_out, clip_start, clip_end)
            if prompts_dir is not None or metadata_dir is not None:
                save_prompt_sidecar(sample_id, caption, prompts_dir, metadata_dir, row_payload)
                prompt_saved += 1
            done += 1
        except subprocess.CalledProcessError:
            errors += 1

    print({
        "requested_rows": len(df) if args.max_downloads == 0 else min(len(df), args.max_downloads),
        "downloaded_or_clipped": done,
        "skipped_existing": skipped,
        "prompt_or_metadata_saved": prompt_saved,
        "errors": errors,
        "clip_dir": str(clip_dir),
        "raw_video_dir": str(raw_dir),
        "prompts_dir": str(prompts_dir) if prompts_dir else "",
        "metadata_dir": str(metadata_dir) if metadata_dir else "",
    })


if __name__ == "__main__":
    main()
