from __future__ import annotations

import json
from pathlib import Path

from tooling.security import hardening_backlog_trigger_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_hardening_backlog_trigger_gate_passes_when_sources_unchanged(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    source = repo / "governance" / "security" / "incident_regression_catalog.json"
    _write(source, '{"incidents":[]}\n')
    state = repo / "governance" / "security" / "hardening_backlog_trigger_state.json"
    _write_json(
        state,
        {"sources": [{"path": "governance/security/incident_regression_catalog.json", "sha256": hardening_backlog_trigger_gate._sha256(source)}]},
    )
    _write(repo / "glyphser_security_hardening_master_todo.txt", "A. Alpha\n[ ] pending\n")

    monkeypatch.setattr(hardening_backlog_trigger_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_backlog_trigger_gate, "STATE", state)
    monkeypatch.setattr(hardening_backlog_trigger_gate, "TODO", repo / "glyphser_security_hardening_master_todo.txt")
    monkeypatch.setattr(hardening_backlog_trigger_gate, "evidence_root", lambda: repo / "evidence")
    assert hardening_backlog_trigger_gate.main([]) == 0


def test_hardening_backlog_trigger_gate_fails_when_new_trigger_detected(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    source = repo / "governance" / "security" / "incident_regression_catalog.json"
    _write(source, '{"incidents":[]}\n')
    state = repo / "governance" / "security" / "hardening_backlog_trigger_state.json"
    _write_json(
        state,
        {"sources": [{"path": "governance/security/incident_regression_catalog.json", "sha256": "0" * 64}]},
    )
    _write(repo / "glyphser_security_hardening_master_todo.txt", "A. Alpha\nDONE\n")

    monkeypatch.setattr(hardening_backlog_trigger_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_backlog_trigger_gate, "STATE", state)
    monkeypatch.setattr(hardening_backlog_trigger_gate, "TODO", repo / "glyphser_security_hardening_master_todo.txt")
    monkeypatch.setattr(hardening_backlog_trigger_gate, "evidence_root", lambda: repo / "evidence")
    assert hardening_backlog_trigger_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "hardening_backlog_trigger_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("new_trigger_detected_append_items_required:") for item in report["findings"])
    assert "done_marker_must_not_be_present_on_new_trigger" in report["findings"]
