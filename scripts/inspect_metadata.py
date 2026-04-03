import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse
from src.metadata.panda70m_index import Panda70MIndex


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    args = ap.parse_args()
    df = Panda70MIndex(args.csv).load()
    print(df.head(5).to_string(index=False))
    print({"rows": len(df), "columns": list(df.columns)})
