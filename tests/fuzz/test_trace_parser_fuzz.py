from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.glyphser.trace.compute_trace_hash import compute_trace_hash


@pytest.mark.fuzz_harness
def test_trace_parser_fuzz():
    root = Path(__file__).resolve().parents[2]
    trace_path = root / "artifacts" / "inputs" / "fixtures" / "hello-core" / "trace.json"
    data = json.loads(trace_path.read_text(encoding="utf-8"))
    a = compute_trace_hash(data)
    b = compute_trace_hash(data)
    assert a == b
