from __future__ import annotations
import json
from pathlib import Path

from generated import operators as gen_ops

ROOT = Path(__file__).resolve().parents[2]
VEC_ROOT = ROOT / "tests" / "conformance" / "vectors" / "operators"

def _load(op_id: str) -> dict:
    path = VEC_ROOT / (op_id.replace(".", "_") + ".json")
    return json.loads(path.read_text(encoding="utf-8"))

def test_glyphser_backend_loaddriver_vector():
    data = _load("Glyphser.Backend.LoadDriver")
    vector = data["vectors"][0]
    expected = vector["expected"]
    stub = getattr(gen_ops, "Glyphser_Backend_LoadDriver")
    result = stub(vector["request"])
    if "error" in expected:
        assert "error" in result
        assert result["error"]["code_id"] == expected["error"]["code_id"]
        assert result["error"]["message"] == expected["error"]["message"]
        for key, val in expected["error"]["context"].items():
            assert result["error"]["context"].get(key) == val
    else:
        assert result == expected["response"]

