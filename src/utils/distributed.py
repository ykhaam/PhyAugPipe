from __future__ import annotations

from typing import Iterable, List, Sequence, TypeVar

T = TypeVar("T")


def shard_items(items: Sequence[T], num_shards: int, shard_id: int) -> List[T]:
    if num_shards <= 1:
        return list(items)
    return [it for i, it in enumerate(items) if i % num_shards == shard_id]


def shard_tag(num_shards: int, shard_id: int) -> str:
    return f"shard-{shard_id:02d}-of-{num_shards:02d}"
