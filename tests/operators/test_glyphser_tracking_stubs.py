from __future__ import annotations
import json
from pathlib import Path

from generated import operators as gen_ops

ROOT = Path(__file__).resolve().parents[2]
VEC_ROOT = ROOT / "tests" / "conformance" / "vectors" / "operators"

def _load(op_id: str) -> dict:
    path = VEC_ROOT / (op_id.replace(".", "_") + ".json")
    return json.loads(path.read_text(encoding="utf-8"))

def test_glyphser_tracking_artifactget_vector():
    data = _load("Glyphser.Tracking.ArtifactGet")
    vector = data["vectors"][0]
    expected = vector["expected"]
    stub = getattr(gen_ops, "Glyphser_Tracking_ArtifactGet")
    result = stub(vector["request"])
    if "error" in expected:
        assert result["error"] == expected["error"]
    else:
        assert result == expected["response"]

def test_glyphser_tracking_artifactlist_vector():
    data = _load("Glyphser.Tracking.ArtifactList")
    vector = data["vectors"][0]
    expected = vector["expected"]
    stub = getattr(gen_ops, "Glyphser_Tracking_ArtifactList")
    result = stub(vector["request"])
    if "error" in expected:
        assert result["error"] == expected["error"]
    else:
        assert result == expected["response"]

def test_glyphser_tracking_artifactput_vector():
    data = _load("Glyphser.Tracking.ArtifactPut")
    vector = data["vectors"][0]
    expected = vector["expected"]
    stub = getattr(gen_ops, "Glyphser_Tracking_ArtifactPut")
    result = stub(vector["request"])
    if "error" in expected:
        assert result["error"] == expected["error"]
    else:
        assert result == expected["response"]

def test_glyphser_tracking_artifacttombstone_vector():
    data = _load("Glyphser.Tracking.ArtifactTombstone")
    vector = data["vectors"][0]
    expected = vector["expected"]
    stub = getattr(gen_ops, "Glyphser_Tracking_ArtifactTombstone")
    result = stub(vector["request"])
    if "error" in expected:
        assert result["error"] == expected["error"]
    else:
        assert result == expected["response"]

def test_glyphser_tracking_metriclog_vector():
    data = _load("Glyphser.Tracking.MetricLog")
    vector = data["vectors"][0]
    expected = vector["expected"]
    stub = getattr(gen_ops, "Glyphser_Tracking_MetricLog")
    result = stub(vector["request"])
    if "error" in expected:
        assert result["error"] == expected["error"]
    else:
        assert result == expected["response"]

def test_glyphser_tracking_runcreate_vector():
    data = _load("Glyphser.Tracking.RunCreate")
    vector = data["vectors"][0]
    expected = vector["expected"]
    stub = getattr(gen_ops, "Glyphser_Tracking_RunCreate")
    result = stub(vector["request"])
    if "error" in expected:
        assert result["error"] == expected["error"]
    else:
        assert result == expected["response"]

def test_glyphser_tracking_runend_vector():
    data = _load("Glyphser.Tracking.RunEnd")
    vector = data["vectors"][0]
    expected = vector["expected"]
    stub = getattr(gen_ops, "Glyphser_Tracking_RunEnd")
    result = stub(vector["request"])
    if "error" in expected:
        assert result["error"] == expected["error"]
    else:
        assert result == expected["response"]

def test_glyphser_tracking_runstart_vector():
    data = _load("Glyphser.Tracking.RunStart")
    vector = data["vectors"][0]
    expected = vector["expected"]
    stub = getattr(gen_ops, "Glyphser_Tracking_RunStart")
    result = stub(vector["request"])
    if "error" in expected:
        assert result["error"] == expected["error"]
    else:
        assert result == expected["response"]

