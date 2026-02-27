from __future__ import annotations

import json
from pathlib import Path

from generated import operators as gen_ops

ROOT = Path(__file__).resolve().parents[1]
VEC_ROOT = ROOT / "tests" / "conformance" / "vectors" / "operators"


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
                assert result["error"] == expected["error"]
            else:
                assert result == expected["response"]
