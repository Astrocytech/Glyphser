from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_workflow_artifact_coverage_validator


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_security_workflow_artifact_coverage_validator_passes_when_uploads_are_produced(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    _write(sec / "alpha_gate.py", 'out = evidence_root() / "security" / "alpha.json"\n')
    workflow = repo / ".github" / "workflows" / "security-maintenance.yml"
    _write(workflow, "path: ${{ env.GLYPHSER_EVIDENCE_ROOT }}/security/alpha.json\n")
    policy = repo / "governance" / "security" / "security_critical_artifacts.json"
    _write(policy, '{"critical_artifacts": ["alpha.json"]}\n')

    monkeypatch.setattr(security_workflow_artifact_coverage_validator, "ROOT", repo)
    monkeypatch.setattr(security_workflow_artifact_coverage_validator, "SECURITY_TOOLING", sec)
    monkeypatch.setattr(security_workflow_artifact_coverage_validator, "WORKFLOW", workflow)
    monkeypatch.setattr(security_workflow_artifact_coverage_validator, "CRITICAL_ARTIFACTS_POLICY", policy)
    monkeypatch.setattr(security_workflow_artifact_coverage_validator, "evidence_root", lambda: repo / "evidence")
    assert security_workflow_artifact_coverage_validator.main([]) == 0


def test_security_workflow_artifact_coverage_validator_fails_on_unmatched_upload(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    _write(sec / "alpha_gate.py", 'out = evidence_root() / "security" / "alpha.json"\n')
    workflow = repo / ".github" / "workflows" / "security-maintenance.yml"
    _write(workflow, "path: ${{ env.GLYPHSER_EVIDENCE_ROOT }}/security/beta.json\n")
    policy = repo / "governance" / "security" / "security_critical_artifacts.json"
    _write(policy, '{"critical_artifacts": ["alpha.json"]}\n')

    monkeypatch.setattr(security_workflow_artifact_coverage_validator, "ROOT", repo)
    monkeypatch.setattr(security_workflow_artifact_coverage_validator, "SECURITY_TOOLING", sec)
    monkeypatch.setattr(security_workflow_artifact_coverage_validator, "WORKFLOW", workflow)
    monkeypatch.setattr(security_workflow_artifact_coverage_validator, "CRITICAL_ARTIFACTS_POLICY", policy)
    monkeypatch.setattr(security_workflow_artifact_coverage_validator, "evidence_root", lambda: repo / "evidence")
    assert security_workflow_artifact_coverage_validator.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "security_workflow_artifact_coverage_validator.json").read_text(encoding="utf-8"))
    assert "uploaded_artifacts_without_producer:1" in report["findings"]
    assert "critical_artifacts_missing_upload:1" in report["findings"]
    assert report["unmatched_uploads"] == ["beta.json"]


def test_security_workflow_artifact_coverage_validator_fails_when_critical_not_uploaded(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    _write(sec / "alpha_gate.py", 'out = evidence_root() / "security" / "alpha.json"\n')
    workflow = repo / ".github" / "workflows" / "security-maintenance.yml"
    _write(workflow, "path: ${{ env.GLYPHSER_EVIDENCE_ROOT }}/security/other.json\n")
    policy = repo / "governance" / "security" / "security_critical_artifacts.json"
    _write(policy, '{"critical_artifacts": ["alpha.json"]}\n')

    monkeypatch.setattr(security_workflow_artifact_coverage_validator, "ROOT", repo)
    monkeypatch.setattr(security_workflow_artifact_coverage_validator, "SECURITY_TOOLING", sec)
    monkeypatch.setattr(security_workflow_artifact_coverage_validator, "WORKFLOW", workflow)
    monkeypatch.setattr(security_workflow_artifact_coverage_validator, "CRITICAL_ARTIFACTS_POLICY", policy)
    monkeypatch.setattr(security_workflow_artifact_coverage_validator, "evidence_root", lambda: repo / "evidence")
    assert security_workflow_artifact_coverage_validator.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "security_workflow_artifact_coverage_validator.json").read_text(encoding="utf-8"))
    assert "critical_artifacts_missing_upload:1" in report["findings"]
