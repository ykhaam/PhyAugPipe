#!/usr/bin/env python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.pipeline.runner import load_config
from src.pipeline.stage1_prefilter import run_stage1_prefilter
from src.utils.io import ensure_dir
from src.utils.logging import setup_logger


def main():
    cfg = load_config("configs/default.yaml", "configs/models.yaml", "configs/scoring.yaml", "configs/panda70m.yaml")
    logger = setup_logger("shortlist", ensure_dir(cfg["run"]["log_dir"]) / "shortlist.log")
    run_stage1_prefilter(cfg, logger)


if __name__ == "__main__":
    main()
