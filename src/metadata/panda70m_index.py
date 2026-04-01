from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import pandas as pd


@dataclass
class Panda70MIndexConfig:
    input_csv: str
    id_field: str = "sample_id"
    split_field: str = "split"
    caption_field: str = "caption"


class Panda70MIndex:
    def __init__(self, cfg: Panda70MIndexConfig):
        self.cfg = cfg

    def load(self) -> pd.DataFrame:
        path = Path(self.cfg.input_csv)
        if not path.exists():
            raise FileNotFoundError(f"Metadata CSV not found: {path}")
        df = pd.read_csv(path)
        required = [self.cfg.id_field, self.cfg.split_field, self.cfg.caption_field]
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"Missing required metadata columns: {missing}")
        return df

    def inspect(self) -> Dict[str, object]:
        df = self.load()
        return {
            "num_rows": len(df),
            "columns": list(df.columns),
            "splits": df[self.cfg.split_field].value_counts(dropna=False).to_dict(),
            "null_caption_count": int(df[self.cfg.caption_field].isna().sum()),
        }
