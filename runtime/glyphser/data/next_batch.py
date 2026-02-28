"""Deterministic next-batch helper (minimal)."""
from __future__ import annotations

from typing import Any, Sequence, Tuple


def next_batch(dataset: Sequence[Any], cursor: int, batch_size: int) -> Tuple[list[Any], int]:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    if cursor < 0:
        raise ValueError("cursor must be non-negative")

    n = len(dataset)
    if n == 0:
        return [], cursor

    end = min(cursor + batch_size, n)
    batch = list(dataset[cursor:end])
    next_cursor = end if end < n else 0
    return batch, next_cursor
