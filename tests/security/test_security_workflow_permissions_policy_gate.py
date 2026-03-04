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
                "    permissions:",
                "      contents: read",
                "      security-events: write",
                "    steps:",
                "      - run: python tooling/security/security_super_gate.py",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (wf / "security-maintenance.yml").write_text(
        "\n".join(
            [
                "jobs:",
                "  security-maintenance:",
                "    permissions:",
                "      contents: read",
                "    steps:",
                "      - run: python tooling/security/security_super_gate.py",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (wf / "security-super-extended.yml").write_text(
        "\n".join(
            [
                "jobs:",
                "  security-super-extended:",
                "    permissions:",
                "      contents: read",
                "    steps:",
                "      - run: python tooling/security/security_super_gate.py --include-extended",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (wf / "release.yml").write_text(
        "\n".join(
            [
                "jobs:",
                "  verify-signatures:",
                "    permissions:",
                "      contents: read",
                "    steps:",
                "      - run: python tooling/security/security_super_gate.py --strict-key",
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
                "    permissions:",
                "      contents: read",
                "      security-events: write",
                "    steps:",
                "      - run: python tooling/security/security_super_gate.py",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (wf / "security-maintenance.yml").write_text(
        "jobs:\n  security-maintenance:\n    permissions:\n      contents: read\n",
        encoding="utf-8",
    )
    (wf / "security-super-extended.yml").write_text(
        "jobs:\n  security-super-extended:\n    permissions:\n      contents: read\n",
        encoding="utf-8",
    )
    (wf / "release.yml").write_text(
        "jobs:\n  verify-signatures:\n    permissions:\n      contents: read\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(security_workflow_permissions_policy_gate, "ROOT", repo)
    monkeypatch.setattr(security_workflow_permissions_policy_gate, "evidence_root", lambda: repo / "evidence")
    assert security_workflow_permissions_policy_gate.main([]) == 1
    report = json.loads((ev / "security_workflow_permissions_policy_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(item.startswith("forbidden_permission_write_all:") for item in report["findings"])


def test_security_workflow_permissions_policy_gate_fails_when_required_job_scope_missing(
    monkeypatch, tmp_path: Path
) -> None:
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
                "    permissions:",
                "      contents: read",
                "    steps:",
                "      - run: python tooling/security/security_super_gate.py",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (wf / "security-maintenance.yml").write_text(
        "jobs:\n  security-maintenance:\n    permissions:\n      contents: read\n",
        encoding="utf-8",
    )
    (wf / "security-super-extended.yml").write_text(
        "jobs:\n  security-super-extended:\n    permissions:\n      contents: read\n",
        encoding="utf-8",
    )
    (wf / "release.yml").write_text(
        "jobs:\n  verify-signatures:\n    permissions:\n      contents: read\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(security_workflow_permissions_policy_gate, "ROOT", repo)
    monkeypatch.setattr(security_workflow_permissions_policy_gate, "evidence_root", lambda: repo / "evidence")
    assert security_workflow_permissions_policy_gate.main([]) == 1
    report = json.loads((ev / "security_workflow_permissions_policy_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    prefix = "missing_required_job_permission:.github/workflows/ci.yml:security-matrix:security-events: write"
    assert any(item.startswith(prefix) for item in report["findings"])
