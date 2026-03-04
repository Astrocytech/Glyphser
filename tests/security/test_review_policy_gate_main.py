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
    assert review_policy_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "review_policy_gate.json").read_text(encoding="utf-8"))
    assert "missing_security_changelog_entry" in report["findings"]


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
    assert review_policy_gate.main([]) == 0
