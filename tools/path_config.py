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
    return rel("artifacts", "inputs", "fixtures")


def vectors_root() -> Path:
    return rel("artifacts", "inputs", "vectors")


def goldens_root() -> Path:
    return rel("artifacts", "expected", "goldens")


def generated_root() -> Path:
    return rel("artifacts", "generated")


def bundles_root() -> Path:
    return rel("artifacts", "bundles")


def evidence_root() -> Path:
    return rel("evidence")


def conformance_reports_root() -> Path:
    return rel("evidence", "conformance", "reports")


def conformance_results_root() -> Path:
    return rel("evidence", "conformance", "results")
