from __future__ import annotations

from pathlib import Path

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
from src.utils.io import load_yaml, ensure_dir
from src.utils.logging import build_logger
from src.vlm.qwen_vl_runner import QwenVLRunner


def run_pipeline(config_path: str, models_path: str, scoring_path: str) -> None:
    cfg = load_yaml(config_path)
    models = load_yaml(models_path)
    scoring_cfg = load_yaml(scoring_path)

    out_root = ensure_dir(Path(cfg["project"]["output_root"]) / cfg["project"]["run_name"])
    logger = build_logger("pipeline", out_root / "run.log")

    rows = stage1_prefilter.run(cfg, out_root, logger)
    rows = stage2_extract_frames.run(cfg, out_root, rows, logger)

    vlm = QwenVLRunner(models)
    stage3_element_parsing.run(cfg, out_root, rows, vlm, logger)
    stage4_vision_checking.run(cfg, out_root, rows, vlm, logger)
    stage5_physics_reasoning.run(cfg, out_root, rows, vlm, logger)
    stage6_scoring.run(cfg, scoring_cfg, out_root, logger)
    stage7_prompt_extending.run(cfg, out_root, rows, vlm, logger)
    stage8_export.run(cfg, scoring_cfg, out_root, rows, logger)


if __name__ == "__main__":
    run_pipeline("configs/default.yaml", "configs/models.yaml", "configs/scoring.yaml")
