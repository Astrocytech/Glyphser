from __future__ import annotations

import json
from pathlib import Path

from tooling.security import policy_schema_validation_gate


def test_policy_schema_validation_gate_passes_for_non_empty_json_objects(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    pol = repo / "governance" / "security"
    pol.mkdir(parents=True)
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    (pol / "a.json").write_text(json.dumps({"k": 1}) + "\n", encoding="utf-8")

    monkeypatch.setattr(policy_schema_validation_gate, "ROOT", repo)
    monkeypatch.setattr(policy_schema_validation_gate, "evidence_root", lambda: repo / "evidence")
    assert policy_schema_validation_gate.main([]) == 0


def test_policy_schema_validation_gate_strict_mode_requires_schema_version(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    pol = repo / "governance" / "security"
    pol.mkdir(parents=True)
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    (pol / "a.json").write_text(json.dumps({"k": 1}) + "\n", encoding="utf-8")

    monkeypatch.setattr(policy_schema_validation_gate, "ROOT", repo)
    monkeypatch.setattr(policy_schema_validation_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_POLICY_SCHEMA_STRICT", "true")
    assert policy_schema_validation_gate.main([]) == 1
    report = json.loads((ev / "policy_schema_validation_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(item.startswith("missing_or_invalid_schema_version:") for item in report["findings"])
