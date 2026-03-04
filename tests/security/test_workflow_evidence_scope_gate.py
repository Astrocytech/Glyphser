from __future__ import annotations

import json
from pathlib import Path

from tooling.security import workflow_evidence_scope_gate


def test_workflow_evidence_scope_gate_detects_missing_guard(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "bad.yml").write_text(
        """
name: bad
jobs:
  j:
    runs-on: ubuntu-latest
    steps:
      - run: python tooling/security/security_artifacts.py
""".strip()
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(workflow_evidence_scope_gate, "ROOT", repo)
    monkeypatch.setattr(workflow_evidence_scope_gate, "WORKFLOWS", wf)
    monkeypatch.setattr(workflow_evidence_scope_gate, "evidence_root", lambda: repo / "evidence")
    assert workflow_evidence_scope_gate.main([]) == 1


def test_workflow_evidence_scope_gate_passes_when_scoped(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "ok.yml").write_text(
        """
name: ok
jobs:
  j:
    env:
      GLYPHSER_EVIDENCE_ROOT: evidence/runs/${{ github.run_id }}/ok
    runs-on: ubuntu-latest
    steps:
      - run: python tooling/security/evidence_run_dir_guard.py --run-id "${{ github.run_id }}-ok"
      - run: python tooling/security/security_artifacts.py
""".strip()
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(workflow_evidence_scope_gate, "ROOT", repo)
    monkeypatch.setattr(workflow_evidence_scope_gate, "WORKFLOWS", wf)
    monkeypatch.setattr(workflow_evidence_scope_gate, "evidence_root", lambda: repo / "evidence")
    assert workflow_evidence_scope_gate.main([]) == 0
    report = json.loads(
        (repo / "evidence" / "security" / "workflow_evidence_scope_gate.json").read_text(encoding="utf-8")
    )
    assert report["status"] == "PASS"


def test_workflow_evidence_scope_gate_fails_on_non_run_scoped_root(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "bad_scope.yml").write_text(
        """
name: bad_scope
jobs:
  j:
    env:
      GLYPHSER_EVIDENCE_ROOT: evidence/security
    runs-on: ubuntu-latest
    steps:
      - run: python tooling/security/evidence_run_dir_guard.py --run-id "${{ github.run_id }}-bad"
      - run: python tooling/security/security_artifacts.py
""".strip()
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(workflow_evidence_scope_gate, "ROOT", repo)
    monkeypatch.setattr(workflow_evidence_scope_gate, "WORKFLOWS", wf)
    monkeypatch.setattr(workflow_evidence_scope_gate, "evidence_root", lambda: repo / "evidence")
    assert workflow_evidence_scope_gate.main([]) == 1
    report = json.loads(
        (repo / "evidence" / "security" / "workflow_evidence_scope_gate.json").read_text(encoding="utf-8")
    )
    assert any("invalid_GLYPHSER_EVIDENCE_ROOT_scope" in item for item in report["findings"])
