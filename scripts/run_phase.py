import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse
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


def load_shortlist_or_build(cfg: dict, out_root: Path, logger) -> pd.DataFrame:
    shortlist_csv = out_root / "metadata_records" / "shortlist.csv"
    if shortlist_csv.exists() and not cfg["modes"].get("overwrite", False):
        return pd.read_csv(shortlist_csv)
    return stage1_prefilter.run(cfg, out_root, logger)


def run_prepare(cfg: dict, out_root: Path, logger) -> pd.DataFrame:
    rows = load_shortlist_or_build(cfg, out_root, logger)
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
