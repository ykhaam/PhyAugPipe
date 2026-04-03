from __future__ import annotations

from typing import Any


def normalize_parse(raw: dict[str, Any]) -> dict[str, Any]:
    keys = ["entities", "materials", "actions", "forces", "outcomes"]
    out: dict[str, Any] = {}
    for k in keys:
        v = raw.get(k, [])
        if isinstance(v, str):
            v = [v]
        out[k] = v if isinstance(v, list) else []
    return out
