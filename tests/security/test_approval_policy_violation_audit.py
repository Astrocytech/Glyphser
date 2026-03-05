from __future__ import annotations

import json
from pathlib import Path

from tooling.security import approval_policy_violation_audit


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    _write(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def test_approval_policy_violation_audit_tracks_new_and_recurring(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _write_json(
        sec / "review_policy_gate.json",
        {
            "status": "FAIL",
            "findings": [
                "split_role_author_is_sole_approver",
                "missing_required_reviewer_group:workflow_changes:release-engineering",
            ],
            "summary": {},
            "metadata": {},
        },
    )
    _write_json(
        sec / "approval_policy_violation_audit_history.json",
        {"open_violations": ["split_role_author_is_sole_approver"]},
    )

    monkeypatch.setattr(approval_policy_violation_audit, "ROOT", repo)
    monkeypatch.setattr(approval_policy_violation_audit, "evidence_root", lambda: repo / "evidence")
    assert approval_policy_violation_audit.main([]) == 0

    report = json.loads((sec / "approval_policy_violation_audit.json").read_text(encoding="utf-8"))
    assert report["status"] == "WARN"
    assert report["summary"]["new_violations"] == ["missing_required_reviewer_group:workflow_changes:release-engineering"]
    assert report["summary"]["recurring_violations"] == ["split_role_author_is_sole_approver"]


def test_approval_policy_violation_audit_tracks_resolution(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _write_json(sec / "review_policy_gate.json", {"status": "PASS", "findings": [], "summary": {}, "metadata": {}})
    _write_json(
        sec / "approval_policy_violation_audit_history.json",
        {"open_violations": ["split_role_author_is_sole_approver"]},
    )

    monkeypatch.setattr(approval_policy_violation_audit, "ROOT", repo)
    monkeypatch.setattr(approval_policy_violation_audit, "evidence_root", lambda: repo / "evidence")
    assert approval_policy_violation_audit.main([]) == 0

    report = json.loads((sec / "approval_policy_violation_audit.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["summary"]["resolved_since_last"] == ["split_role_author_is_sole_approver"]
