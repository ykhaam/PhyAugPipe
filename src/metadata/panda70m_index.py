from __future__ import annotations

from pathlib import Path
import pandas as pd


class Panda70MIndex:
    def __init__(self, csv_path: str | Path):
        self.csv_path = Path(csv_path)

    def load(self) -> pd.DataFrame:
        return pd.read_csv(self.csv_path)

    def smoke_subset(self, df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
        return df.head(n).copy()
