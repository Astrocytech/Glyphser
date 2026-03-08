from __future__ import annotations

import json
from pathlib import Path

from tooling.security import file_permission_matrix_gate


def _write(path: Path, text: str, mode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    path.chmod(mode)


def test_file_permission_matrix_gate_emits_sensitive_output_parity_hash(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(repo / "evidence" / "security" / "sbom.json", "{}", 0o640)
    _write(repo / "evidence" / "security" / "build_provenance.json", "{}", 0o640)
    _write(repo / "governance" / "security" / "review_policy.json", "{}", 0o644)

    monkeypatch.setattr(file_permission_matrix_gate, "ROOT", repo)
    monkeypatch.setattr(file_permission_matrix_gate, "evidence_root", lambda: repo / "evidence")
    assert file_permission_matrix_gate.main([]) == 0

    report = json.loads((repo / "evidence" / "security" / "file_permission_matrix_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["parity_hash"]
    assert report["summary"]["sensitive_outputs_present"] == 3
    assert len(report["summary"]["sensitive_outputs"]) == 3


def test_file_permission_matrix_gate_fails_on_writable_sensitive_output(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(repo / "evidence" / "security" / "sbom.json", "{}", 0o666)
    _write(repo / "evidence" / "security" / "build_provenance.json", "{}", 0o640)
    _write(repo / "governance" / "security" / "review_policy.json", "{}", 0o644)

    monkeypatch.setattr(file_permission_matrix_gate, "ROOT", repo)
    monkeypatch.setattr(file_permission_matrix_gate, "evidence_root", lambda: repo / "evidence")
    assert file_permission_matrix_gate.main([]) == 1

    report = json.loads((repo / "evidence" / "security" / "file_permission_matrix_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(str(item).startswith("group_or_world_writable:evidence/security/sbom.json:") for item in report["findings"])
