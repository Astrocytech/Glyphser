from __future__ import annotations

from src.glyphser.error.emit import emit_error


def test_emit_error_stable_shape():
    err = emit_error("CONTRACT_VIOLATION", "bad", b=2, a=1)
    assert err["code_id"] == "CONTRACT_VIOLATION"
    assert err["message"] == "bad"
    assert list(err["context"].keys()) == ["a", "b"]
