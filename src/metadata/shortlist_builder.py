from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List

import pandas as pd


@dataclass
class ShortlistConfig:
    splits: List[str]
    desirable_only: bool
    desirable_values: List[Any]
    single_shot_only: bool
    single_shot_values: List[Any]
    min_duration_sec: float
    max_duration_sec: float
    sports_dynamics_keywords: List[str]
    keyword_mode: str = "any"


class ShortlistBuilder:
    def __init__(self, fields: Dict[str, str], cfg: ShortlistConfig):
        self.fields = fields
        self.cfg = cfg

    def build(self, df: pd.DataFrame) -> pd.DataFrame:
        w = df.copy()
        tags_col: List[List[str]] = []
        keep_mask: List[bool] = []

        for _, row in w.iterrows():
            tags: List[str] = []
            keep = True

            split = str(row.get(self.fields["split_field"], ""))
            if self.cfg.splits and split not in self.cfg.splits:
                keep = False
            else:
                tags.append("split_ok")

            desirability = str(row.get(self.fields.get("desirability_field", "desirability"), "")).lower()
            if self.cfg.desirable_only:
                allowed = {str(v).lower() for v in self.cfg.desirable_values}
                if desirability not in allowed:
                    keep = False
                else:
                    tags.append("desirable_ok")

            shot_val = str(row.get(self.fields.get("shot_count_field", "shot_count"), "")).lower()
            if self.cfg.single_shot_only:
                allowed = {str(v).lower() for v in self.cfg.single_shot_values}
                if shot_val not in allowed:
                    keep = False
                else:
                    tags.append("single_shot_ok")

            duration = row.get(self.fields.get("duration_field", "duration_sec"), None)
            if pd.notna(duration):
                d = float(duration)
                if d < self.cfg.min_duration_sec or d > self.cfg.max_duration_sec:
                    keep = False
                else:
                    tags.append("duration_ok")

            caption = str(row.get(self.fields["caption_field"], "")).lower()
            kw_hits = [k for k in self.cfg.sports_dynamics_keywords if k.lower() in caption]
            if self.cfg.sports_dynamics_keywords:
                if self.cfg.keyword_mode == "any" and not kw_hits:
                    keep = False
                elif self.cfg.keyword_mode == "all" and len(kw_hits) < len(self.cfg.sports_dynamics_keywords):
                    keep = False
                else:
                    tags.append(f"keyword_hits:{'|'.join(kw_hits)}")

            tags_col.append(tags)
            keep_mask.append(keep)

        w["shortlist_tags"] = tags_col
        w["shortlist_pass"] = keep_mask
        return w[w["shortlist_pass"]].reset_index(drop=True)
