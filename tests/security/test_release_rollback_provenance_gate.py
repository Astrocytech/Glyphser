from __future__ import annotations

import json
from pathlib import Path

from tooling.security import release_rollback_provenance_gate


def _write_status(path: Path, status: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"status": status}) + "\n", encoding="utf-8")


def test_release_rollback_provenance_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    deploy = repo / "evidence" / "deploy"
    _write_status(deploy / "latest.json", "PASS")
    _write_status(deploy / "rollback.json", "PASS")
    _write_status(sec / "provenance_signature.json", "PASS")
    _write_status(sec / "policy_signature.json", "PASS")

    monkeypatch.setattr(release_rollback_provenance_gate, "ROOT", repo)
    monkeypatch.setattr(release_rollback_provenance_gate, "evidence_root", lambda: repo / "evidence")
    assert release_rollback_provenance_gate.main([]) == 0


def test_release_rollback_provenance_gate_fails_when_any_dependency_not_pass(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    deploy = repo / "evidence" / "deploy"
    _write_status(deploy / "latest.json", "PASS")
    _write_status(deploy / "rollback.json", "FAIL")
    _write_status(sec / "provenance_signature.json", "PASS")
    _write_status(sec / "policy_signature.json", "PASS")

    monkeypatch.setattr(release_rollback_provenance_gate, "ROOT", repo)
    monkeypatch.setattr(release_rollback_provenance_gate, "evidence_root", lambda: repo / "evidence")
    assert release_rollback_provenance_gate.main([]) == 1
