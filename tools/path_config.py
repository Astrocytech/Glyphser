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


def fixtures_root() -> Path:
    return first_existing([rel("artifacts", "inputs", "fixtures"), rel("fixtures")])


def vectors_root() -> Path:
    return first_existing([rel("artifacts", "inputs", "vectors"), rel("vectors")])


def goldens_root() -> Path:
    return first_existing([rel("artifacts", "expected", "goldens"), rel("goldens")])


def generated_root() -> Path:
    return first_existing([rel("artifacts", "generated"), rel("generated")])


def bundles_root() -> Path:
    return first_existing([rel("artifacts", "bundles"), rel("dist")])


def evidence_root() -> Path:
    return first_existing([rel("evidence"), rel("reports")])
