from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_workflow_permissions_policy_gate


def test_security_workflow_permissions_policy_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    wf = repo / ".github" / "workflows"
    ev = repo / "evidence" / "security"
    wf.mkdir(parents=True)
    ev.mkdir(parents=True)
    (wf / "ci.yml").write_text(
        "\n".join(
            [
                "permissions:",
                "  contents: read",
                "jobs:",
                "  security-matrix:",
                "    steps:",
                "      - run: python tooling/security/security_super_gate.py",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(security_workflow_permissions_policy_gate, "ROOT", repo)
    monkeypatch.setattr(security_workflow_permissions_policy_gate, "evidence_root", lambda: repo / "evidence")
    assert security_workflow_permissions_policy_gate.main([]) == 0


def test_security_workflow_permissions_policy_gate_fails_on_write_all(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    wf = repo / ".github" / "workflows"
    ev = repo / "evidence" / "security"
    wf.mkdir(parents=True)
    ev.mkdir(parents=True)
    (wf / "ci.yml").write_text(
        "\n".join(
            [
                "permissions: write-all",
                "jobs:",
                "  security-matrix:",
                "    steps:",
                "      - run: python tooling/security/security_super_gate.py",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(security_workflow_permissions_policy_gate, "ROOT", repo)
    monkeypatch.setattr(security_workflow_permissions_policy_gate, "evidence_root", lambda: repo / "evidence")
    assert security_workflow_permissions_policy_gate.main([]) == 1
    report = json.loads((ev / "security_workflow_permissions_policy_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(item.startswith("forbidden_permission_write_all:") for item in report["findings"])
