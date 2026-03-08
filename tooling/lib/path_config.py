from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]


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
    return rel("artifacts", "inputs", "conformance")


def goldens_root() -> Path:
    return rel("artifacts", "expected", "goldens")


def generated_root() -> Path:
    return rel("artifacts", "generated", "stable")


def generated_codegen_root() -> Path:
    return generated_tmp_root() / "codegen"


def generated_build_metadata_root() -> Path:
    return generated_root() / "metadata"


def generated_tmp_root() -> Path:
    return rel("artifacts", "generated", "tmp")


def generated_runtime_state_root() -> Path:
    # Backward-compatible alias kept for existing callers.
    return runtime_state_root()


def bundles_root() -> Path:
    return rel("artifacts", "bundles")


def evidence_root() -> Path:
    override = os.environ.get("GLYPHSER_EVIDENCE_ROOT", "").strip()
    if override:
        path = Path(override)
        return path if path.is_absolute() else rel(override)
    return rel("evidence")


def evidence_runtime_state_root() -> Path:
    return runtime_state_root()


def runtime_state_root() -> Path:
    return rel("artifacts", "inputs", "reference_states")


def conformance_reports_root() -> Path:
    return rel("evidence", "conformance", "reports")


def conformance_results_root() -> Path:
    return rel("evidence", "conformance", "results")
