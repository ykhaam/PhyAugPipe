from __future__ import annotations

from typing import Any, Dict


def ensure_parse_schema(parsed: Dict[str, Any]) -> Dict[str, Any]:
    keys = ["entities", "materials", "actions", "forces", "outcomes"]
    out: Dict[str, Any] = {}
    for k in keys:
        v = parsed.get(k, [])
        if not isinstance(v, list):
            v = [v] if v else []
        out[k] = v
    return out
