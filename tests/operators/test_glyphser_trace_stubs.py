from __future__ import annotations
import json
from pathlib import Path

from generated import operators as gen_ops

ROOT = Path(__file__).resolve().parents[2]
VEC_ROOT = ROOT / "tests" / "conformance" / "vectors" / "operators"

def _load(op_id: str) -> dict:
    path = VEC_ROOT / (op_id.replace(".", "_") + ".json")
    return json.loads(path.read_text(encoding="utf-8"))

def test_glyphser_trace_tracemigrate_vector():
    data = _load("Glyphser.Trace.TraceMigrate")
    vector = data["vectors"][0]
    expected = vector["expected"]
    stub = getattr(gen_ops, "Glyphser_Trace_TraceMigrate")
    result = stub(vector["request"])
    if "error" in expected:
        assert result["error"] == expected["error"]
    else:
        assert result == expected["response"]

