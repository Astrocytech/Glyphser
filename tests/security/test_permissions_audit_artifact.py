from __future__ import annotations

import json
from pathlib import Path

from tooling.security import permissions_audit_artifact


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_permissions_audit_artifact_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(
        repo / ".github" / "workflows" / "ci.yml",
        "permissions:\n  contents: read\njobs:\n  test:\n    runs-on: ubuntu-latest\n",
    )

    monkeypatch.setattr(permissions_audit_artifact, "ROOT", repo)
    monkeypatch.setattr(permissions_audit_artifact, "WORKFLOWS", repo / ".github/workflows")
    monkeypatch.setattr(permissions_audit_artifact, "evidence_root", lambda: repo / "evidence")

    assert permissions_audit_artifact.main([]) == 0
    report = json.loads((repo / "evidence" / "security" / "permissions_audit_artifact.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"


def test_permissions_audit_artifact_warns_on_write_all(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(
        repo / ".github" / "workflows" / "ci.yml",
        "permissions: write-all\njobs:\n  test:\n    runs-on: ubuntu-latest\n",
    )

    monkeypatch.setattr(permissions_audit_artifact, "ROOT", repo)
    monkeypatch.setattr(permissions_audit_artifact, "WORKFLOWS", repo / ".github/workflows")
    monkeypatch.setattr(permissions_audit_artifact, "evidence_root", lambda: repo / "evidence")

    assert permissions_audit_artifact.main([]) == 0
    report = json.loads((repo / "evidence" / "security" / "permissions_audit_artifact.json").read_text(encoding="utf-8"))
    assert report["status"] == "WARN"
    assert "workflow_permissions_write_all:ci.yml" in report["findings"]
