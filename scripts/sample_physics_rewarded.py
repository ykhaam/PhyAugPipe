import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse

import pandas as pd


def main() -> None:
    ap = argparse.ArgumentParser(description="Data sampling with physics rewarding")
    ap.add_argument("--input-csv", required=True, help="all_scored_samples.csv or passed_winners.csv")
    ap.add_argument("--output-csv", required=True)
    ap.add_argument("--sample-size", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--alpha", type=float, default=2.0, help="Reward strength for high physics_richness")
    args = ap.parse_args()

    df = pd.read_csv(args.input_csv)
    if "physics_richness" not in df.columns:
        raise ValueError("physics_richness column is required")

    scores = df["physics_richness"].fillna(0.0).clip(lower=0.0).astype(float)
    weights = (scores + 1e-6) ** args.alpha
    n = min(args.sample_size, len(df))
    sampled = df.sample(n=n, weights=weights, random_state=args.seed)

    out = Path(args.output_csv)
    out.parent.mkdir(parents=True, exist_ok=True)
    sampled.to_csv(out, index=False)
    print({"input_rows": len(df), "sampled_rows": len(sampled), "output_csv": str(out), "alpha": args.alpha})


if __name__ == "__main__":
    main()
