import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse

from src.metadata.panda70m_index import Panda70MIndex


def main() -> None:
    ap = argparse.ArgumentParser(description="Normalize Panda train_2m.csv to pipeline format and optionally take top-N rows")
    ap.add_argument("--input-csv", required=True)
    ap.add_argument("--output-csv", required=True)
    ap.add_argument("--top-n", type=int, default=0, help="If >0, keep first N rows after normalization")
    args = ap.parse_args()

    idx = Panda70MIndex(args.input_csv)
    df = idx.load()
    if args.top_n > 0:
        df = df.head(args.top_n).copy()

    out = Path(args.output_csv)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print({"rows": len(df), "output_csv": str(out), "top_n": args.top_n})


if __name__ == "__main__":
    main()
