from __future__ import annotations

import pandas as pd


FALLBACK_PROMPT_FIELDS = ("caption", "original_caption", "text", "prompt")


def resolve_prompt_field(df: pd.DataFrame, configured_field: str | None = None) -> str:
    candidates: list[str] = []
    if configured_field:
        candidates.append(configured_field)
    candidates.extend([f for f in FALLBACK_PROMPT_FIELDS if f not in candidates])

    for field in candidates:
        if field in df.columns:
            return field
    raise ValueError(
        f"No prompt/text field found. Tried configured field={configured_field!r} and fallbacks={list(FALLBACK_PROMPT_FIELDS)}"
    )


def attach_original_caption_column(df: pd.DataFrame, configured_field: str | None = None) -> tuple[pd.DataFrame, str]:
    field = resolve_prompt_field(df, configured_field)
    out = df.copy()
    out["original_caption"] = out[field].fillna("").astype(str)
    if "caption" not in out.columns:
        out["caption"] = out["original_caption"]
    return out, field
