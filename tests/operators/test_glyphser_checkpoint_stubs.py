from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser._generated import operators as gen_ops

ROOT = Path(__file__).resolve().parents[2]
VEC_ROOT = ROOT / "artifacts" / "inputs" / "conformance" / "primitive_vectors" / "operators"


def _load(op_id: str) -> dict:
    path = VEC_ROOT / (op_id.replace(".", "_") + ".json")
    return json.loads(path.read_text(encoding="utf-8"))


def test_glyphser_checkpoint_checkpointmigrate_vector():
    data = _load("Glyphser.Checkpoint.CheckpointMigrate")
    vector = data["vectors"][0]
    expected = vector["expected"]
    stub = getattr(gen_ops, "Glyphser_Checkpoint_CheckpointMigrate")
    result = stub(vector["request"])
    if "error" in expected:
        assert "error" in result
        assert result["error"]["code_id"] == expected["error"]["code_id"]
        assert result["error"]["message"] == expected["error"]["message"]
        for key, val in expected["error"]["context"].items():
            assert result["error"]["context"].get(key) == val
    else:
        assert result == expected["response"]


def test_glyphser_checkpoint_restore_vector():
    data = _load("Glyphser.Checkpoint.Restore")
    vector = data["vectors"][0]
    expected = vector["expected"]
    stub = getattr(gen_ops, "Glyphser_Checkpoint_Restore")
    result = stub(vector["request"])
    if "error" in expected:
        assert "error" in result
        assert result["error"]["code_id"] == expected["error"]["code_id"]
        assert result["error"]["message"] == expected["error"]["message"]
        for key, val in expected["error"]["context"].items():
            assert result["error"]["context"].get(key) == val
    else:
        assert result == expected["response"]
