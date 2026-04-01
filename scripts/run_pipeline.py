#!/usr/bin/env python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import argparse

from src.pipeline.runner import load_config, run_pipeline


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke-test", action="store_true")
    ap.add_argument("--num-shards", type=int, default=1)
    ap.add_argument("--shard-id", type=int, default=0)
    args = ap.parse_args()

    cfg = load_config("configs/default.yaml", "configs/models.yaml", "configs/scoring.yaml", "configs/panda70m.yaml")
    cfg["run"]["smoke_test"] = args.smoke_test
    cfg["execution"]["num_shards"] = args.num_shards
    cfg["execution"]["shard_id"] = args.shard_id
    run_pipeline(cfg)


if __name__ == "__main__":
    main()
