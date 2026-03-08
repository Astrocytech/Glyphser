from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import workflow_pin_change_approval_gate


def _write_approval(repo: Path) -> None:
    approval = repo / "governance" / "security" / "workflow_pin_change_approval.json"
    approval.parent.mkdir(parents=True, exist_ok=True)
    approval.write_text(
        json.dumps(
            {
                "ticket": "SEC-123",
                "rationale": "Pin updates approved after security review.",
                "approved_by": "security-ops",
                "approved_at_utc": "2026-03-01T00:00:00+00:00",
                "expires_at_utc": "2099-01-01T00:00:00+00:00",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    approval.with_suffix(".json.sig").write_text(
        sign_file(approval, key=current_key(strict=False)) + "\n",
        encoding="utf-8",
    )


def test_workflow_pin_change_approval_gate_skips_when_no_pin_change(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(workflow_pin_change_approval_gate, "ROOT", repo)
    monkeypatch.setattr(workflow_pin_change_approval_gate, "APPROVAL_FILE", repo / "governance/security/a.json")
    monkeypatch.setattr(workflow_pin_change_approval_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(workflow_pin_change_approval_gate, "_pin_refs_changed", lambda: False)
    monkeypatch.setattr(workflow_pin_change_approval_gate, "_changed_files", lambda: [])
    assert workflow_pin_change_approval_gate.main([]) == 0


def test_workflow_pin_change_approval_gate_fails_without_approval(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(workflow_pin_change_approval_gate, "ROOT", repo)
    monkeypatch.setattr(
        workflow_pin_change_approval_gate,
        "APPROVAL_FILE",
        repo / "governance/security/workflow_pin_change_approval.json",
    )
    monkeypatch.setattr(workflow_pin_change_approval_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(workflow_pin_change_approval_gate, "_pin_refs_changed", lambda: True)
    monkeypatch.setattr(workflow_pin_change_approval_gate, "_changed_files", lambda: [".github/workflows/ci.yml"])
    assert workflow_pin_change_approval_gate.main([]) == 1


def test_workflow_pin_change_approval_gate_passes_with_signed_approval(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_approval(repo)
    monkeypatch.setattr(workflow_pin_change_approval_gate, "ROOT", repo)
    monkeypatch.setattr(
        workflow_pin_change_approval_gate,
        "APPROVAL_FILE",
        repo / "governance/security/workflow_pin_change_approval.json",
    )
    monkeypatch.setattr(workflow_pin_change_approval_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(workflow_pin_change_approval_gate, "_pin_refs_changed", lambda: True)
    monkeypatch.setattr(
        workflow_pin_change_approval_gate,
        "_changed_files",
        lambda: [
            ".github/workflows/ci.yml",
            "governance/security/workflow_pin_change_approval.json",
            "governance/security/workflow_pin_change_approval.json.sig",
        ],
    )
    assert workflow_pin_change_approval_gate.main([]) == 0
