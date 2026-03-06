from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_event_schema_gate


def _seed_schema(repo: Path) -> Path:
    schema = repo / "governance" / "security" / "security_event_schema.json"
    schema.parent.mkdir(parents=True, exist_ok=True)
    schema.write_text(
        json.dumps(
            {
                "required_fields": ["event_type", "severity", "control_id", "run_id", "artifact_ref"],
                "allowed_severities": ["low", "medium", "high"],
                "event_type": "security_gate_status",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return schema


def test_security_event_schema_gate_passes_valid_events(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    schema = _seed_schema(repo)
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    (sec / "security_events.jsonl").write_text(
        json.dumps(
            {
                "event_type": "security_gate_status",
                "severity": "high",
                "control_id": "gate_a",
                "run_id": "r1",
                "artifact_ref": "evidence/security/gate_a.json",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(security_event_schema_gate, "ROOT", repo)
    monkeypatch.setattr(security_event_schema_gate, "SCHEMA", schema)
    monkeypatch.setattr(security_event_schema_gate, "evidence_root", lambda: repo / "evidence")
    assert security_event_schema_gate.main([]) == 0


def test_security_event_schema_gate_fails_invalid_severity(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    schema = _seed_schema(repo)
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    (sec / "security_events.jsonl").write_text(
        json.dumps(
            {
                "event_type": "security_gate_status",
                "severity": "critical",
                "control_id": "gate_a",
                "run_id": "r1",
                "artifact_ref": "evidence/security/gate_a.json",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(security_event_schema_gate, "ROOT", repo)
    monkeypatch.setattr(security_event_schema_gate, "SCHEMA", schema)
    monkeypatch.setattr(security_event_schema_gate, "evidence_root", lambda: repo / "evidence")
    assert security_event_schema_gate.main([]) == 1


def test_security_event_schema_gate_fails_when_fail_report_has_no_event(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    schema = _seed_schema(repo)
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    (sec / "gate_a.json").write_text(json.dumps({"status": "FAIL"}) + "\n", encoding="utf-8")
    (sec / "security_events.jsonl").write_text("", encoding="utf-8")
    monkeypatch.setattr(security_event_schema_gate, "ROOT", repo)
    monkeypatch.setattr(security_event_schema_gate, "SCHEMA", schema)
    monkeypatch.setattr(security_event_schema_gate, "evidence_root", lambda: repo / "evidence")
    assert security_event_schema_gate.main([]) == 1
    report = json.loads((sec / "security_event_schema_gate.json").read_text(encoding="utf-8"))
    assert "missing_fail_event_payload:evidence/security/gate_a.json" in report["findings"]


def test_security_event_schema_gate_passes_when_fail_report_has_event(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    schema = _seed_schema(repo)
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    (sec / "gate_a.json").write_text(json.dumps({"status": "FAIL"}) + "\n", encoding="utf-8")
    (sec / "security_events.jsonl").write_text(
        json.dumps(
            {
                "event_type": "security_gate_status",
                "severity": "high",
                "control_id": "gate_a",
                "run_id": "r1",
                "artifact_ref": "evidence/security/gate_a.json",
                "status": "FAIL",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(security_event_schema_gate, "ROOT", repo)
    monkeypatch.setattr(security_event_schema_gate, "SCHEMA", schema)
    monkeypatch.setattr(security_event_schema_gate, "evidence_root", lambda: repo / "evidence")
    assert security_event_schema_gate.main([]) == 0
