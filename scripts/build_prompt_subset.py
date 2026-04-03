import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse
import ast
import random

import pandas as pd


DEFAULT_SPORTS_KEYWORDS = [
    "soccer", "football", "basketball", "baseball", "tennis", "volleyball", "hockey", "rugby",
    "athlete", "runner", "running", "jump", "kick", "throw", "spin", "bounce", "race",
    "stadium", "field", "court", "gym", "swim", "cycling", "skate", "ski",
]


def to_sec(hms: str) -> float:
    h, m, s = hms.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def explode_train2m(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in df.iterrows():
        vid = r.get("videoID")
        url = r.get("url")
        ts_list = ast.literal_eval(r["timestamp"]) if isinstance(r.get("timestamp"), str) else []
        cap_list = ast.literal_eval(r["caption"]) if isinstance(r.get("caption"), str) else []
        ms_list = ast.literal_eval(r["matching_score"]) if isinstance(r.get("matching_score"), str) else []

        n = min(len(ts_list), len(cap_list))
        for i in range(n):
            st, ed = ts_list[i]
            rows.append({
                "sample_id": f"{vid}_c{i}",
                "split": "train",
                "caption": cap_list[i],
                "desirability": 1,
                "shot_count": 1,
                "duration_sec": max(0.0, to_sec(ed) - to_sec(st)),
                "video_path": f"{vid}.mp4",
                "videoID": vid,
                "url": url,
                "clip_start": st,
                "clip_end": ed,
                "matching_score": ms_list[i] if i < len(ms_list) else None,
            })
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description="Build sports-focused prompt subset from Panda-70M train_2m CSV")
    ap.add_argument("--input-csv", required=True, help="Path to Panda train_2m.csv")
    ap.add_argument("--output-csv", required=True, help="Output flattened and filtered CSV")
    ap.add_argument("--max-samples", type=int, default=30000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--keywords", nargs="*", default=DEFAULT_SPORTS_KEYWORDS)
    args = ap.parse_args()

    random.seed(args.seed)
    df = pd.read_csv(args.input_csv)

    if {"videoID", "timestamp", "caption"}.issubset(df.columns):
        df = explode_train2m(df)

    kw = [k.lower() for k in args.keywords]
    mask = df["caption"].fillna("").str.lower().apply(lambda x: any(k in x for k in kw))
    filtered = df[mask].copy()

    filtered = filtered.sample(frac=1.0, random_state=args.seed).reset_index(drop=True)
    if args.max_samples > 0:
        filtered = filtered.head(args.max_samples)

    out_path = Path(args.output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    filtered.to_csv(out_path, index=False)

    print({
        "input_rows": len(df),
        "keyword_rows": int(mask.sum()),
        "output_rows": len(filtered),
        "output_csv": str(out_path),
    })


if __name__ == "__main__":
    main()
