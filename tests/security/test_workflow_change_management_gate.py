from __future__ import annotations

import json
from pathlib import Path

from tooling.security import workflow_change_management_gate


def test_workflow_change_management_gate_fails_without_policy_diff_or_rationale(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(workflow_change_management_gate, "ROOT", repo)
    monkeypatch.setattr(workflow_change_management_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_CHANGED_FILES", ".github/workflows/security-maintenance.yml")
    monkeypatch.delenv("GLYPHSER_WORKFLOW_CHANGE_RATIONALE", raising=False)
    assert workflow_change_management_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "workflow_change_management_gate.json").read_text("utf-8"))
    assert report["status"] == "FAIL"
    assert "security_workflow_change_missing_policy_diff_or_rationale" in report["findings"]


def test_workflow_change_management_gate_passes_with_policy_diff(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(workflow_change_management_gate, "ROOT", repo)
    monkeypatch.setattr(workflow_change_management_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv(
        "GLYPHSER_CHANGED_FILES",
        ".github/workflows/security-maintenance.yml,governance/security/promotion_policy.json",
    )
    monkeypatch.delenv("GLYPHSER_WORKFLOW_CHANGE_RATIONALE", raising=False)
    assert workflow_change_management_gate.main([]) == 0
