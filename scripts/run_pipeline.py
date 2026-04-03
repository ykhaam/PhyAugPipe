import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.pipeline.runner import run_pipeline


if __name__ == "__main__":
    run_pipeline("configs/default.yaml", "configs/models.yaml", "configs/scoring.yaml")
