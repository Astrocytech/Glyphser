from __future__ import annotations

import json
from pathlib import Path

from tooling.security import branch_protection_policy_gate


def test_branch_protection_policy_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True)
    (repo / ".github" / "branch-protection.required.json").write_text(
        json.dumps(
            {
                "required_status_checks": ["test-matrix", "security-matrix", "branch-protection-policy"],
                "required_release_checks": ["build", "verify-signatures"],
                "required_workflow_jobs": {"reproducible-build.yml": ["reproducible-build"]},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (wf / "ci.yml").write_text(
        "jobs:\n  test-matrix:\n    runs-on: ubuntu-latest\n  security-matrix:\n    runs-on: ubuntu-latest\n  branch-protection-policy:\n    runs-on: ubuntu-latest\n",
        encoding="utf-8",
    )
    (wf / "release.yml").write_text(
        "jobs:\n  build:\n    runs-on: ubuntu-latest\n  verify-signatures:\n    runs-on: ubuntu-latest\n",
        encoding="utf-8",
    )
    (wf / "reproducible-build.yml").write_text(
        "jobs:\n  reproducible-build:\n    runs-on: ubuntu-latest\n", encoding="utf-8"
    )

    monkeypatch.setattr(branch_protection_policy_gate, "ROOT", repo)
    monkeypatch.setattr(branch_protection_policy_gate, "evidence_root", lambda: repo / "evidence")
    rc = branch_protection_policy_gate.main()
    assert rc == 0


def test_branch_protection_policy_gate_fails_when_job_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True)
    (repo / ".github" / "branch-protection.required.json").write_text(
        json.dumps({"required_status_checks": ["security-matrix"], "required_release_checks": []}) + "\n",
        encoding="utf-8",
    )
    (wf / "ci.yml").write_text("jobs:\n  test-matrix:\n    runs-on: ubuntu-latest\n", encoding="utf-8")
    (wf / "release.yml").write_text("jobs:\n  build:\n    runs-on: ubuntu-latest\n", encoding="utf-8")

    monkeypatch.setattr(branch_protection_policy_gate, "ROOT", repo)
    monkeypatch.setattr(branch_protection_policy_gate, "evidence_root", lambda: repo / "evidence")
    rc = branch_protection_policy_gate.main()
    assert rc == 1


def test_branch_protection_policy_gate_fails_when_critical_policy_checks_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True)
    (repo / ".github" / "branch-protection.required.json").write_text(
        json.dumps(
            {
                "required_status_checks": ["test-matrix", "security-matrix"],
                "required_release_checks": ["build"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (wf / "ci.yml").write_text(
        "jobs:\n  test-matrix:\n    runs-on: ubuntu-latest\n  security-matrix:\n    runs-on: ubuntu-latest\n",
        encoding="utf-8",
    )
    (wf / "release.yml").write_text("jobs:\n  build:\n    runs-on: ubuntu-latest\n", encoding="utf-8")

    monkeypatch.setattr(branch_protection_policy_gate, "ROOT", repo)
    monkeypatch.setattr(branch_protection_policy_gate, "evidence_root", lambda: repo / "evidence")
    rc = branch_protection_policy_gate.main()
    assert rc == 1
    report = json.loads((repo / "evidence" / "security" / "branch_protection_policy.json").read_text(encoding="utf-8"))
    assert "branch-protection-policy" in report["missing_policy_status_checks"]
    assert "verify-signatures" in report["missing_policy_release_checks"]
