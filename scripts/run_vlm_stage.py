import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse
import json
from pathlib import Path

from src.utils.distributed import filter_shard
from src.vlm.qwen_vl_runner import QwenVLRunner
from src.pipeline import stage3_element_parsing, stage4_vision_checking, stage5_physics_reasoning, stage7_prompt_extending
from src.utils.io import load_yaml
import pandas as pd

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["element_parsing", "vision_checking", "physics_reasoning", "prompt_extending"], required=True)
    ap.add_argument("--shard-id", type=int, default=0)
    ap.add_argument("--num-shards", type=int, default=1)
    args = ap.parse_args()

    cfg = load_yaml("configs/default.yaml")
    models = load_yaml("configs/models.yaml")
    out_root = Path(cfg["project"]["output_root"]) / cfg["project"]["run_name"]
    short = pd.read_csv(out_root / "metadata_records" / "shortlist.csv")
    shard_rows = pd.DataFrame(filter_shard(short.to_dict(orient="records"), args.shard_id, args.num_shards))

    vlm = QwenVLRunner(models)
    class L:
        def info(self, *a, **k): print(*a)
    logger = L()

    if args.stage == "element_parsing":
        stage3_element_parsing.run(cfg, out_root, shard_rows, vlm, logger)
    elif args.stage == "vision_checking":
        stage4_vision_checking.run(cfg, out_root, shard_rows, vlm, logger)
    elif args.stage == "physics_reasoning":
        stage5_physics_reasoning.run(cfg, out_root, shard_rows, vlm, logger)
    else:
        stage7_prompt_extending.run(cfg, out_root, shard_rows, vlm, logger)

    print(json.dumps({"stage": args.stage, "shard": args.shard_id, "num_shards": args.num_shards}))
