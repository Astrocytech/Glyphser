from __future__ import annotations

import json
from pathlib import Path

from tooling.security import docs_workflow_reference_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_docs_workflow_reference_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(
        repo / ".github" / "workflows" / "ci.yml",
        "jobs:\n  security:\n    steps:\n      - name: Security scan\n        run: echo ok\n",
    )
    _write(
        repo / "governance" / "security" / "WORKFLOW_STEP_REFERENCES.md",
        "- `.github/workflows/ci.yml#step:Security scan`\n",
    )
    monkeypatch.setattr(docs_workflow_reference_gate, "ROOT", repo)
    monkeypatch.setattr(docs_workflow_reference_gate, "DOC_ROOTS", (repo / "governance" / "security",))
    monkeypatch.setattr(docs_workflow_reference_gate, "evidence_root", lambda: repo / "evidence")
    assert docs_workflow_reference_gate.main([]) == 0


def test_docs_workflow_reference_gate_fails_when_step_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(
        repo / ".github" / "workflows" / "ci.yml",
        "jobs:\n  security:\n    steps:\n      - name: Security scan\n        run: echo ok\n",
    )
    _write(
        repo / "governance" / "security" / "WORKFLOW_STEP_REFERENCES.md",
        "- `.github/workflows/ci.yml#step:Nonexistent step`\n",
    )
    monkeypatch.setattr(docs_workflow_reference_gate, "ROOT", repo)
    monkeypatch.setattr(docs_workflow_reference_gate, "DOC_ROOTS", (repo / "governance" / "security",))
    monkeypatch.setattr(docs_workflow_reference_gate, "evidence_root", lambda: repo / "evidence")
    assert docs_workflow_reference_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "docs_workflow_reference_gate.json").read_text(encoding="utf-8"))
    assert any(item.startswith("missing_workflow_step_reference:") for item in report["findings"])
