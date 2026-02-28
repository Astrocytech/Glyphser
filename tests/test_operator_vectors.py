from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser._generated import operators as gen_ops

ROOT = Path(__file__).resolve().parents[1]
VEC_ROOT = ROOT / "artifacts" / "inputs" / "conformance" / "primitive_vectors" / "operators"


def test_operator_vectors_stub_errors():
    for vec_file in sorted(VEC_ROOT.glob("*.json")):
        payload = json.loads(vec_file.read_text(encoding="utf-8"))
        operator_id = payload.get("operator_id")
        assert operator_id
        func_name = operator_id.replace(".", "_")
        stub = getattr(gen_ops, func_name)
        for vector in payload.get("vectors", []):
            expected = vector["expected"]
            result = stub(vector["request"])
            if "error" in expected:
                assert "error" in result
                assert result["error"]["code_id"] == expected["error"]["code_id"]
                assert result["error"]["message"] == expected["error"]["message"]
                for key, val in expected["error"]["context"].items():
                    assert result["error"]["context"].get(key) == val
            else:
                assert result == expected["response"]
