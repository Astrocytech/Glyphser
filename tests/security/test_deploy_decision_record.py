from __future__ import annotations

import json
from pathlib import Path

from tooling.security import deploy_decision_record


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_deploy_decision_record_passes_with_run_approvers_and_digest(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _write(sec / "security_super_gate.json", {"status": "PASS"})
    monkeypatch.setattr(deploy_decision_record, "ROOT", repo)
    monkeypatch.setattr(deploy_decision_record, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GITHUB_RUN_ID", "123456")
    monkeypatch.setenv("GLYPHSER_DEPLOY_APPROVERS", "security-team,release-manager")
    assert deploy_decision_record.main([]) == 0
    gate = json.loads((sec / "deploy_decision_record_gate.json").read_text("utf-8"))
    assert gate["status"] == "PASS"
    record = json.loads((sec / "deploy_decision_record.json").read_text("utf-8"))
    assert record["run_id"] == "123456"
    assert record["approvers"] == ["security-team", "release-manager"]


def test_deploy_decision_record_fails_without_required_fields(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(deploy_decision_record, "ROOT", repo)
    monkeypatch.setattr(deploy_decision_record, "evidence_root", lambda: repo / "evidence")
    monkeypatch.delenv("GITHUB_RUN_ID", raising=False)
    monkeypatch.delenv("GLYPHSER_RUN_ID", raising=False)
    monkeypatch.setenv("GLYPHSER_DEPLOY_APPROVERS", "")
    assert deploy_decision_record.main([]) == 1
