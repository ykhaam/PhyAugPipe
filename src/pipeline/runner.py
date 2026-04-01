from __future__ import annotations

from pathlib import Path
from typing import Dict

from src.pipeline.stage1_prefilter import run_stage1_prefilter
from src.pipeline.stage2_extract_frames import run_stage2_extract_frames
from src.pipeline.stage3_element_parsing import run_stage3_element_parsing
from src.pipeline.stage4_vision_checking import run_stage4_vision_checking
from src.pipeline.stage5_physics_reasoning import run_stage5_physics_reasoning
from src.pipeline.stage6_scoring import run_stage6_scoring
from src.pipeline.stage7_prompt_extending import run_stage7_prompt_extending
from src.pipeline.stage8_export import run_stage8_export
from src.utils.distributed import shard_tag
from src.utils.io import ensure_dir, load_yaml
from src.utils.logging import setup_logger
from src.vlm.qwen_vl_runner import QwenVLConfig, QwenVLRunner


def load_config(default_cfg: str, models_cfg: str, scoring_cfg: str, panda_cfg: str) -> Dict:
    cfg = load_yaml(default_cfg)
    cfg["models"] = load_yaml(models_cfg)
    cfg["scoring"] = load_yaml(scoring_cfg)
    cfg["panda70m"] = load_yaml(panda_cfg)
    return cfg


def run_pipeline(config: Dict) -> None:
    log_dir = ensure_dir(config["run"].get("log_dir", "artifacts/logs"))
    shard = shard_tag(config["execution"]["num_shards"], config["execution"]["shard_id"])
    logger = setup_logger("phyaugpipe", log_dir / f"pipeline_{shard}.log")
    logger.info("Starting pipeline with %s", shard)

    runner = QwenVLRunner(QwenVLConfig(**config["models"]["vlm"]), enable_model=False)

    stages = config["pipeline"]["stages"]
    if "prefilter" in stages:
        run_stage1_prefilter(config, logger)
    if "extract_frames" in stages:
        run_stage2_extract_frames(config, logger)
    if "element_parsing" in stages:
        run_stage3_element_parsing(config, logger, runner)
    if "vision_checking" in stages:
        run_stage4_vision_checking(config, logger, runner)
    if "physics_reasoning" in stages:
        run_stage5_physics_reasoning(config, logger, runner)
    if "scoring" in stages:
        run_stage6_scoring(config, logger)
    if "prompt_extending" in stages:
        run_stage7_prompt_extending(config, logger, runner)
    if "export" in stages:
        run_stage8_export(config, logger)

    logger.info("Pipeline complete for %s", shard)
