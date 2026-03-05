from __future__ import annotations

import json
from pathlib import Path

from tooling.security import artifact_path_case_conflict_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_artifact_path_case_conflict_gate_passes_without_conflicts(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(
        repo / ".github" / "workflows" / "ci.yml",
        "path: |\n  evidence/security/report.json\n  evidence/security/report.json.sig\n",
    )

    monkeypatch.setattr(artifact_path_case_conflict_gate, "ROOT", repo)
    monkeypatch.setattr(artifact_path_case_conflict_gate, "WORKFLOWS", repo / ".github" / "workflows")
    monkeypatch.setattr(artifact_path_case_conflict_gate, "EVIDENCE_SECURITY", repo / "evidence" / "security")
    monkeypatch.setattr(artifact_path_case_conflict_gate, "evidence_root", lambda: repo / "evidence")

    assert artifact_path_case_conflict_gate.main([]) == 0


def test_artifact_path_case_conflict_gate_detects_workflow_conflict(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(
        repo / ".github" / "workflows" / "ci.yml",
        "path: |\n  evidence/security/Foo.json\n  evidence/security/foo.json\n",
    )

    monkeypatch.setattr(artifact_path_case_conflict_gate, "ROOT", repo)
    monkeypatch.setattr(artifact_path_case_conflict_gate, "WORKFLOWS", repo / ".github" / "workflows")
    monkeypatch.setattr(artifact_path_case_conflict_gate, "EVIDENCE_SECURITY", repo / "evidence" / "security")
    monkeypatch.setattr(artifact_path_case_conflict_gate, "evidence_root", lambda: repo / "evidence")

    assert artifact_path_case_conflict_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "artifact_path_case_conflict_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(item.startswith("workflow_case_conflict:") for item in report["findings"])
