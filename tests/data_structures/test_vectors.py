from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.glyphser.data_structures.validate_struct import (
    validate_checkpoint_header,
    validate_trace_iter_record,
)

ROOT = Path(__file__).resolve().parents[2]
VECTORS = ROOT / "conformance" / "vectors" / "struct_validation" / "vectors.json"


def _validate(struct: str, obj) -> None:
    if struct == "TraceIterRecord":
        validate_trace_iter_record(obj)
        return
    if struct == "CheckpointHeader":
        validate_checkpoint_header(obj)
        return
    raise ValueError(f"unknown struct: {struct}")


def test_struct_vectors():
    data = json.loads(VECTORS.read_text(encoding="utf-8"))
    for vector in data["vectors"]:
        struct = vector["struct"]
        obj = vector["input"]
        expected = vector["expected"]
        if expected == "valid":
            _validate(struct, obj)
        else:
            with pytest.raises((TypeError, ValueError)):
                _validate(struct, obj)
