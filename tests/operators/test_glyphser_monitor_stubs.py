from __future__ import annotations
import json
from pathlib import Path

from generated import operators as gen_ops

ROOT = Path(__file__).resolve().parents[2]
VEC_ROOT = ROOT / "tests" / "conformance" / "vectors" / "operators"

def _load(op_id: str) -> dict:
    path = VEC_ROOT / (op_id.replace(".", "_") + ".json")
    return json.loads(path.read_text(encoding="utf-8"))

def test_glyphser_monitor_driftcompute_stub_error():
    data = _load("Glyphser.Monitor.DriftCompute")
    vector = data["vectors"][0]
    expected = vector["expected"]["error"]
    stub = getattr(gen_ops, "Glyphser_Monitor_DriftCompute")
    result = stub(vector["request"])
    assert result["error"] == expected

def test_glyphser_monitor_emit_stub_error():
    data = _load("Glyphser.Monitor.Emit")
    vector = data["vectors"][0]
    expected = vector["expected"]["error"]
    stub = getattr(gen_ops, "Glyphser_Monitor_Emit")
    result = stub(vector["request"])
    assert result["error"] == expected

def test_glyphser_monitor_register_stub_error():
    data = _load("Glyphser.Monitor.Register")
    vector = data["vectors"][0]
    expected = vector["expected"]["error"]
    stub = getattr(gen_ops, "Glyphser_Monitor_Register")
    result = stub(vector["request"])
    assert result["error"] == expected

