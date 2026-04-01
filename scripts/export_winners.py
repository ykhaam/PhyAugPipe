import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from pathlib import Path
import pandas as pd
from src.pipeline.stage8_export import run
from src.utils.io import load_yaml

if __name__ == "__main__":
    cfg = load_yaml("configs/default.yaml")
    scoring = load_yaml("configs/scoring.yaml")
    out_root = Path(cfg["project"]["output_root"]) / cfg["project"]["run_name"]
    rows = pd.read_csv(out_root / "metadata_records" / "shortlist.csv")
    class L:
        def info(self, *a, **k): print(*a)
    run(cfg, scoring, out_root, rows, L())
