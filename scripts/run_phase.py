import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse
import random
import subprocess
import pandas as pd

from src.pipeline import (
    stage1_prefilter,
    stage2_extract_frames,
    stage3_element_parsing,
    stage4_vision_checking,
    stage5_physics_reasoning,
    stage6_scoring,
    stage7_prompt_extending,
    stage8_export,
)
from src.utils.io import ensure_dir, load_yaml
from src.utils.logging import build_logger
from src.vlm.qwen_vl_runner import QwenVLRunner


def maybe_filter_csv_for_prepare(cfg: dict, logger) -> None:
    prepare_cfg = cfg.get("prepare", {}).get("csv_filter", {})
    if not prepare_cfg.get("enabled", False):
        return

    input_csv = prepare_cfg["input_csv"]
    output_csv = prepare_cfg["output_csv"]
    max_samples = int(prepare_cfg.get("max_samples", 30000))
    seed = int(prepare_cfg.get("seed", 42))
    keywords = [str(k).lower() for k in prepare_cfg.get("keywords", [])]
    caption_field = prepare_cfg.get("caption_field", "caption")

    random.seed(seed)
    df = pd.read_csv(input_csv)
    if caption_field not in df.columns:
        raise ValueError(f"caption field '{caption_field}' not found in {input_csv}")

    if keywords:
        mask = df[caption_field].fillna("").astype(str).str.lower().apply(lambda x: any(k in x for k in keywords))
        df = df[mask].copy()

    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    if max_samples > 0:
        df = df.head(max_samples).copy()

    out = Path(output_csv)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    cfg["io"]["metadata_csv"] = str(out)
    if prepare_cfg.get("disable_stage1_filters", True):
        cfg.setdefault("shortlist", {})["apply_filters"] = False
    logger.info("prepare.csv_filter completed rows=%s output=%s", len(df), out)


def maybe_download_videos_for_prepare(cfg: dict, logger, shortlist_csv: str | None = None) -> None:
    prepare_cfg = cfg.get("prepare", {}).get("video_download", {})
    if not prepare_cfg.get("enabled", False):
        return

    provider = prepare_cfg.get("provider", "video2dataset")
    if provider != "video2dataset":
        raise ValueError("prepare.video_download currently supports only provider=video2dataset (yt-dlp is intentionally separate).")

    csv_path = prepare_cfg.get("csv", "") or shortlist_csv or cfg["io"]["metadata_csv"]
    output_folder = prepare_cfg["output_folder"]
    config_path = prepare_cfg.get("config", "video2dataset/video2dataset/configs/panda70m.yaml")
    extra_columns = prepare_cfg.get("extra_columns", "[matching_score,desirable_filtering,shot_boundary_detection]")
    url_col = prepare_cfg.get("url_col", "url")
    caption_col = prepare_cfg.get("caption_col", "caption")
    clip_col = prepare_cfg.get("clip_col", "timestamp")

    cmd = [
        "video2dataset",
        f"--url_list={csv_path}",
        f"--url_col={url_col}",
        f"--caption_col={caption_col}",
        f"--clip_col={clip_col}",
        f"--output_folder={output_folder}",
        f"--save_additional_columns={extra_columns}",
        f"--config={config_path}",
    ]
    logger.info("prepare.video_download running: %s", " ".join(cmd))
    subprocess.run(cmd, check=True)


def load_shortlist_or_build(cfg: dict, out_root: Path, logger) -> pd.DataFrame:
    shortlist_csv = out_root / "metadata_records" / "shortlist.csv"
    if shortlist_csv.exists() and not cfg["modes"].get("overwrite", False):
        return pd.read_csv(shortlist_csv)
    return stage1_prefilter.run(cfg, out_root, logger)


def run_prepare(cfg: dict, out_root: Path, logger) -> pd.DataFrame:
    maybe_filter_csv_for_prepare(cfg, logger)
    rows = load_shortlist_or_build(cfg, out_root, logger)
    maybe_download_videos_for_prepare(cfg, logger, shortlist_csv=str(out_root / "metadata_records" / "shortlist.csv"))
    rows = stage2_extract_frames.run(cfg, out_root, rows, logger)
    return rows


def run_data_filtering_5steps(cfg: dict, models: dict, scoring_cfg: dict, out_root: Path, logger) -> pd.DataFrame:
    rows = run_prepare(cfg, out_root, logger)
    vlm = QwenVLRunner(models)
    stage3_element_parsing.run(cfg, out_root, rows, vlm, logger)
    stage4_vision_checking.run(cfg, out_root, rows, vlm, logger)
    stage5_physics_reasoning.run(cfg, out_root, rows, vlm, logger)
    stage6_scoring.run(cfg, scoring_cfg, out_root, logger)
    stage7_prompt_extending.run(cfg, out_root, rows, vlm, logger)
    return rows


def run_export_only(cfg: dict, scoring_cfg: dict, out_root: Path, logger) -> None:
    shortlist_csv = out_root / "metadata_records" / "shortlist.csv"
    if not shortlist_csv.exists():
        raise FileNotFoundError(f"shortlist not found: {shortlist_csv}")
    rows = pd.read_csv(shortlist_csv)
    stage8_export.run(cfg, scoring_cfg, out_root, rows, logger)


def main() -> None:
    ap = argparse.ArgumentParser(description="Run phased pipeline for easier testing")
    ap.add_argument(
        "--phase",
        choices=["prepare", "data_filtering_5steps", "export", "all"],
        required=True,
        help="prepare: stage1-2, data_filtering_5steps: stage3-7, export: stage8, all: stage1-8",
    )
    ap.add_argument("--config", default="configs/default.yaml")
    ap.add_argument("--models", default="configs/models.yaml")
    ap.add_argument("--scoring", default="configs/scoring.yaml")
    args = ap.parse_args()

    cfg = load_yaml(args.config)
    models = load_yaml(args.models)
    scoring_cfg = load_yaml(args.scoring)

    out_root = ensure_dir(Path(cfg["project"]["output_root"]) / cfg["project"]["run_name"])
    logger = build_logger("pipeline.phase", out_root / "run_phase.log")

    if args.phase == "prepare":
        run_prepare(cfg, out_root, logger)
    elif args.phase == "data_filtering_5steps":
        run_data_filtering_5steps(cfg, models, scoring_cfg, out_root, logger)
    elif args.phase == "export":
        run_export_only(cfg, scoring_cfg, out_root, logger)
    else:
        rows = run_data_filtering_5steps(cfg, models, scoring_cfg, out_root, logger)
        stage8_export.run(cfg, scoring_cfg, out_root, rows, logger)


if __name__ == "__main__":
    main()
