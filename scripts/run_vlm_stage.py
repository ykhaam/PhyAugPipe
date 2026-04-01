#!/usr/bin/env python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import argparse

from src.pipeline.runner import load_config
from src.pipeline.stage3_element_parsing import run_stage3_element_parsing
from src.pipeline.stage4_vision_checking import run_stage4_vision_checking
from src.pipeline.stage5_physics_reasoning import run_stage5_physics_reasoning
from src.pipeline.stage6_scoring import run_stage6_scoring
from src.pipeline.stage7_prompt_extending import run_stage7_prompt_extending
from src.utils.io import ensure_dir
from src.utils.logging import setup_logger
from src.vlm.qwen_vl_runner import QwenVLConfig, QwenVLRunner


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["parse", "check", "reason", "score", "prompt", "all"])
    ap.add_argument("--num-shards", type=int, default=1)
    ap.add_argument("--shard-id", type=int, default=0)
    args = ap.parse_args()

    cfg = load_config("configs/default.yaml", "configs/models.yaml", "configs/scoring.yaml", "configs/panda70m.yaml")
    cfg["execution"]["num_shards"] = args.num_shards
    cfg["execution"]["shard_id"] = args.shard_id
    logger = setup_logger("vlm", ensure_dir(cfg["run"]["log_dir"]) / f"vlm_shard{args.shard_id}.log")
    runner = QwenVLRunner(QwenVLConfig(**cfg["models"]["vlm"]), enable_model=False)

    if args.stage in {"parse", "all"}:
        run_stage3_element_parsing(cfg, logger, runner)
    if args.stage in {"check", "all"}:
        run_stage4_vision_checking(cfg, logger, runner)
    if args.stage in {"reason", "all"}:
        run_stage5_physics_reasoning(cfg, logger, runner)
    if args.stage in {"score", "all"}:
        run_stage6_scoring(cfg, logger)
    if args.stage in {"prompt", "all"}:
        run_stage7_prompt_extending(cfg, logger, runner)


if __name__ == "__main__":
    main()
