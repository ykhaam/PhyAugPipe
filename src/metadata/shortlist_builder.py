from __future__ import annotations

import re

import pandas as pd

from src.metadata.prompt_fields import FALLBACK_PROMPT_FIELDS


class ShortlistBuilder:
    def __init__(self, keywords: list[str]):
        self.keywords = [k.lower() for k in keywords]
        variants = [rf"{re.escape(k)}(?:s|es|ed|ing|er)?" for k in self.keywords]
        self._keyword_pattern = re.compile(r"\b(?:" + "|".join(variants) + r")\b")

    def build(
        self,
        df: pd.DataFrame,
        desirable_only: bool,
        single_shot_only: bool,
        sports_dynamics_only: bool,
        duration_min_sec: float,
        duration_max_sec: float,
        random_shuffle: bool = False,
        random_seed: int = 42,
        max_samples: int | None = None,
    ) -> pd.DataFrame:
        out = df.copy()
        if desirable_only and "desirability" in out.columns:
            out = out[out["desirability"].fillna(0).astype(float) > 0]
        if single_shot_only and "shot_count" in out.columns:
            out = out[out["shot_count"].fillna(99).astype(float) <= 1]
        if "duration_sec" in out.columns:
            dur = out["duration_sec"].fillna(0).astype(float)
            out = out[(dur >= duration_min_sec) & (dur <= duration_max_sec)]
        if sports_dynamics_only:
            text_field = next((f for f in FALLBACK_PROMPT_FIELDS if f in out.columns), None)
            if text_field is None:
                raise ValueError(f"sports_dynamics_only=True but none of prompt fields are present: {list(FALLBACK_PROMPT_FIELDS)}")
            text = out[text_field].fillna("").str.lower()
            mask = text.str.contains(self._keyword_pattern)
            out = out[mask]

        if random_shuffle:
            out = out.sample(frac=1.0, random_state=random_seed).reset_index(drop=True)
        if max_samples is not None and max_samples > 0:
            out = out.head(max_samples).copy()
        return out
