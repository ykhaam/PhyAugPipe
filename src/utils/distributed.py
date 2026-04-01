from __future__ import annotations

import hashlib
from typing import Any


def shard_index(sample_id: str, num_shards: int) -> int:
    h = hashlib.md5(sample_id.encode("utf-8")).hexdigest()
    return int(h, 16) % num_shards


def filter_shard(rows: list[dict[str, Any]], shard_id: int, num_shards: int) -> list[dict[str, Any]]:
    return [r for r in rows if shard_index(str(r["sample_id"]), num_shards) == shard_id]
