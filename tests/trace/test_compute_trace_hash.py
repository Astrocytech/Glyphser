from __future__ import annotations

from src.glyphser.trace.compute_trace_hash import compute_trace_hash


def test_compute_trace_hash_deterministic():
    records = [
        {"step": 1, "operator_id": "Glyphser.Data.NextBatch", "event_hash": "aaa"},
        {"step": 1, "operator_id": "Glyphser.Model.ModelIR_Executor", "event_hash": "bbb"},
    ]
    a = compute_trace_hash(records)
    b = compute_trace_hash(records)
    assert a == b
