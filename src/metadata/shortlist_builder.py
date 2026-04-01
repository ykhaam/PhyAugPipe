from __future__ import annotations

import pandas as pd


class ShortlistBuilder:
    def __init__(self, keywords: list[str]):
        self.keywords = [k.lower() for k in keywords]

    def build(
        self,
        df: pd.DataFrame,
        desirable_only: bool,
        single_shot_only: bool,
        sports_dynamics_only: bool,
        duration_min_sec: float,
        duration_max_sec: float,
    ) -> pd.DataFrame:
        out = df.copy()
        if desirable_only and "desirability" in out.columns:
            out = out[out["desirability"].fillna(0).astype(float) > 0]
        if single_shot_only and "shot_count" in out.columns:
            out = out[out["shot_count"].fillna(99).astype(float) <= 1]
        if "duration_sec" in out.columns:
            dur = out["duration_sec"].fillna(0).astype(float)
            out = out[(dur >= duration_min_sec) & (dur <= duration_max_sec)]
        if sports_dynamics_only and "caption" in out.columns:
            text = out["caption"].fillna("").str.lower()
            mask = text.apply(lambda x: any(k in x for k in self.keywords))
            out = out[mask]
        return out
