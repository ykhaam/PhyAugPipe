from __future__ import annotations

from tqdm import tqdm


def progress(iterable, desc: str):
    return tqdm(iterable, desc=desc)
