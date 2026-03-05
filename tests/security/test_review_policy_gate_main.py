from __future__ import annotations

import json
from pathlib import Path

from tooling.security import review_policy_gate


def _write_minimum_repo(repo: Path) -> None:
    (repo / "governance" / "security").mkdir(parents=True, exist_ok=True)
    (repo / ".github").mkdir(parents=True, exist_ok=True)
    (repo / ".github" / "CODEOWNERS").write_text(
        "/tooling/security/ @sec\n/governance/security/ @sec\n/.github/workflows/ @sec\n/runtime/glyphser/security/ @sec\n",
        encoding="utf-8",
    )
    (repo / ".github" / "branch-protection.required.json").write_text(
        json.dumps({"minimum_required_approvals": 2}) + "\n",
        encoding="utf-8",
    )
    (repo / "governance" / "security" / "review_policy.json").write_text(
        json.dumps(
            {
                "required_codeowners_paths": [
                    "tooling/security/**",
                    "governance/security/**",
                    ".github/workflows/**",
                    "runtime/glyphser/security/**",
                ],
                "minimum_required_approvals": 2,
                "required_changelog_file": "governance/security/SECURITY_CHANGELOG.md",
                "security_baseline_paths": [],
                "required_change_ticket_patterns": ["SEC-"],
                "enforce_change_ticket": True,
                "enforce_changelog_entry": True,
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_review_policy_gate_fails_without_security_changelog_for_security_path_changes(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    _write_minimum_repo(repo)
    monkeypatch.setattr(review_policy_gate, "ROOT", repo)
    monkeypatch.setattr(review_policy_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        review_policy_gate,
        "_run",
        lambda _cmd: "runtime/glyphser/security/example.py\n",
    )
    monkeypatch.delenv("GLYPHSER_CHANGE_TICKET", raising=False)
    assert review_policy_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "review_policy_gate.json").read_text(encoding="utf-8"))
    assert "missing_security_changelog_entry" in report["findings"]
    assert "security_change_missing_ticket_or_adr" in report["findings"]


def test_review_policy_gate_passes_when_security_changelog_present(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_minimum_repo(repo)
    monkeypatch.setattr(review_policy_gate, "ROOT", repo)
    monkeypatch.setattr(review_policy_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        review_policy_gate,
        "_run",
        lambda _cmd: "runtime/glyphser/security/example.py\ngovernance/security/SECURITY_CHANGELOG.md\n",
    )
    monkeypatch.setenv("GLYPHSER_CHANGE_TICKET", "SEC-1234")
    assert review_policy_gate.main([]) == 0


def test_review_policy_gate_fails_when_author_is_sole_approver_for_security_critical_change(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    _write_minimum_repo(repo)
    monkeypatch.setattr(review_policy_gate, "ROOT", repo)
    monkeypatch.setattr(review_policy_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        review_policy_gate,
        "_run",
        lambda _cmd: "tooling/security/new_gate.py\ngovernance/security/SECURITY_CHANGELOG.md\n",
    )
    monkeypatch.setenv("GLYPHSER_CHANGE_TICKET", "SEC-1234")
    monkeypatch.setenv("GLYPHSER_PR_AUTHOR", "alice")
    monkeypatch.setenv("GLYPHSER_PR_APPROVERS", "alice")
    assert review_policy_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "review_policy_gate.json").read_text(encoding="utf-8"))
    assert "split_role_author_is_sole_approver" in report["findings"]
    assert "reviewer_independence_author_is_sole_reviewer" in report["findings"]


def test_review_policy_gate_passes_when_distinct_approver_exists_for_security_critical_change(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    _write_minimum_repo(repo)
    monkeypatch.setattr(review_policy_gate, "ROOT", repo)
    monkeypatch.setattr(review_policy_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        review_policy_gate,
        "_run",
        lambda _cmd: "tooling/security/new_gate.py\ngovernance/security/SECURITY_CHANGELOG.md\n",
    )
    monkeypatch.setenv("GLYPHSER_CHANGE_TICKET", "SEC-1234")
    monkeypatch.setenv("GLYPHSER_PR_AUTHOR", "alice")
    monkeypatch.setenv("GLYPHSER_PR_APPROVERS", "alice,bob")
    assert review_policy_gate.main([]) == 0


def test_review_policy_gate_fails_when_approval_is_stale_after_security_change(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    _write_minimum_repo(repo)
    monkeypatch.setattr(review_policy_gate, "ROOT", repo)
    monkeypatch.setattr(review_policy_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        review_policy_gate,
        "_run",
        lambda _cmd: "tooling/security/new_gate.py\ngovernance/security/SECURITY_CHANGELOG.md\n",
    )
    monkeypatch.setenv("GLYPHSER_CHANGE_TICKET", "SEC-1234")
    monkeypatch.setenv("GLYPHSER_PR_AUTHOR", "alice")
    monkeypatch.setenv("GLYPHSER_PR_APPROVERS", "alice,bob")
    monkeypatch.setenv("GLYPHSER_APPROVAL_GRANTED_AT_UTC", "2026-03-01T10:00:00+00:00")
    monkeypatch.setenv("GLYPHSER_LAST_SECURITY_CHANGE_AT_UTC", "2026-03-01T10:05:00+00:00")
    assert review_policy_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "review_policy_gate.json").read_text(encoding="utf-8"))
    assert "approval_stale_post_approval_changes_detected" in report["findings"]


def test_review_policy_gate_passes_when_approval_is_fresh_for_security_change(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    _write_minimum_repo(repo)
    monkeypatch.setattr(review_policy_gate, "ROOT", repo)
    monkeypatch.setattr(review_policy_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        review_policy_gate,
        "_run",
        lambda _cmd: "tooling/security/new_gate.py\ngovernance/security/SECURITY_CHANGELOG.md\n",
    )
    monkeypatch.setenv("GLYPHSER_CHANGE_TICKET", "SEC-1234")
    monkeypatch.setenv("GLYPHSER_PR_AUTHOR", "alice")
    monkeypatch.setenv("GLYPHSER_PR_APPROVERS", "alice,bob")
    monkeypatch.setenv("GLYPHSER_APPROVAL_GRANTED_AT_UTC", "2026-03-01T10:05:00+00:00")
    monkeypatch.setenv("GLYPHSER_LAST_SECURITY_CHANGE_AT_UTC", "2026-03-01T10:00:00+00:00")
    assert review_policy_gate.main([]) == 0


def test_review_policy_gate_fails_when_required_competency_group_missing(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    _write_minimum_repo(repo)
    monkeypatch.setattr(review_policy_gate, "ROOT", repo)
    monkeypatch.setattr(review_policy_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        review_policy_gate,
        "_run",
        lambda _cmd: ".github/workflows/release.yml\ngovernance/security/SECURITY_CHANGELOG.md\n",
    )
    monkeypatch.setenv("GLYPHSER_CHANGE_TICKET", "SEC-1234")
    monkeypatch.setenv("GLYPHSER_PR_AUTHOR", "alice")
    monkeypatch.setenv("GLYPHSER_PR_APPROVERS", "bob,charlie")
    monkeypatch.setenv("GLYPHSER_PR_APPROVER_GROUPS", "security-governance")
    monkeypatch.setenv("GLYPHSER_APPROVAL_GRANTED_AT_UTC", "2026-03-01T10:05:00+00:00")
    monkeypatch.setenv("GLYPHSER_LAST_SECURITY_CHANGE_AT_UTC", "2026-03-01T10:00:00+00:00")
    assert review_policy_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "review_policy_gate.json").read_text(encoding="utf-8"))
    assert any(item.startswith("missing_required_reviewer_group:workflow_changes:") for item in report["findings"])


def test_review_policy_gate_passes_when_required_competency_group_present(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    _write_minimum_repo(repo)
    monkeypatch.setattr(review_policy_gate, "ROOT", repo)
    monkeypatch.setattr(review_policy_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        review_policy_gate,
        "_run",
        lambda _cmd: ".github/workflows/release.yml\ngovernance/security/SECURITY_CHANGELOG.md\n",
    )
    monkeypatch.setenv("GLYPHSER_CHANGE_TICKET", "SEC-1234")
    monkeypatch.setenv("GLYPHSER_PR_AUTHOR", "alice")
    monkeypatch.setenv("GLYPHSER_PR_APPROVERS", "bob,charlie")
    monkeypatch.setenv("GLYPHSER_PR_APPROVER_GROUPS", "release-engineering,security-governance")
    monkeypatch.setenv("GLYPHSER_APPROVAL_GRANTED_AT_UTC", "2026-03-01T10:05:00+00:00")
    monkeypatch.setenv("GLYPHSER_LAST_SECURITY_CHANGE_AT_UTC", "2026-03-01T10:00:00+00:00")
    assert review_policy_gate.main([]) == 0
