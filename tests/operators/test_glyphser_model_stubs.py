from __future__ import annotations
import json
from pathlib import Path

from runtime.glyphser._generated import operators as gen_ops

ROOT = Path(__file__).resolve().parents[2]
VEC_ROOT = ROOT / "artifacts" / "inputs" / "conformance" / "primitives" / "operators"

def _load(op_id: str) -> dict:
    path = VEC_ROOT / (op_id.replace(".", "_") + ".json")
    return json.loads(path.read_text(encoding="utf-8"))

def test_glyphser_model_forward_vector():
    data = _load("Glyphser.Model.Forward")
    vector = data["vectors"][0]
    expected = vector["expected"]
    stub = getattr(gen_ops, "Glyphser_Model_Forward")
    result = stub(vector["request"])
    if "error" in expected:
        assert "error" in result
        assert result["error"]["code_id"] == expected["error"]["code_id"]
        assert result["error"]["message"] == expected["error"]["message"]
        for key, val in expected["error"]["context"].items():
            assert result["error"]["context"].get(key) == val
    else:
        assert result == expected["response"]

def test_glyphser_model_modelir_executor_vector():
    data = _load("Glyphser.Model.ModelIR_Executor")
    vector = data["vectors"][0]
    expected = vector["expected"]
    stub = getattr(gen_ops, "Glyphser_Model_ModelIR_Executor")
    result = stub(vector["request"])
    if "error" in expected:
        assert "error" in result
        assert result["error"]["code_id"] == expected["error"]["code_id"]
        assert result["error"]["message"] == expected["error"]["message"]
        for key, val in expected["error"]["context"].items():
            assert result["error"]["context"].get(key) == val
    else:
        assert result == expected["response"]

