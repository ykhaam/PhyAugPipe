from __future__ import annotations

import ast
from pathlib import Path
import pandas as pd


class Panda70MIndex:
    def __init__(self, csv_path: str | Path):
        self.csv_path = Path(csv_path)

    def load(self) -> pd.DataFrame:
        df = pd.read_csv(self.csv_path)
        return self.normalize_for_pipeline(df)

    @staticmethod
    def _to_sec(hms: str) -> float:
        h, m, s = hms.split(":")
        return int(h) * 3600 + int(m) * 60 + float(s)

    @classmethod
    def normalize_for_pipeline(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Convert Panda train_2m raw rows to pipeline-ready clip rows when needed.

        Raw format columns:
        - videoID, url, timestamp(list), caption(list), matching_score(list)
        """
        raw_cols = {"videoID", "url", "timestamp", "caption", "matching_score"}
        if not raw_cols.issubset(set(df.columns)):
            return df

        rows: list[dict] = []
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
                    "duration_sec": max(0.0, cls._to_sec(ed) - cls._to_sec(st)),
                    "video_path": f"{vid}.mp4",
                    "videoID": vid,
                    "url": url,
                    "clip_start": st,
                    "clip_end": ed,
                    "matching_score": ms_list[i] if i < len(ms_list) else None,
                })
        return pd.DataFrame(rows)

    def smoke_subset(self, df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
        return df.head(n).copy()
