from __future__ import annotations

from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]


def rel(*parts: str) -> Path:
    return ROOT.joinpath(*parts)


def first_existing(candidates: Iterable[Path]) -> Path:
    items = list(candidates)
    for path in items:
        if path.exists():
            return path
    return items[0]
