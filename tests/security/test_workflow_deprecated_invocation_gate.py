from __future__ import annotations

import json
from pathlib import Path

from tooling.security import workflow_deprecated_invocation_gate


def test_workflow_deprecated_invocation_gate_passes_without_deprecated_patterns(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True)
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    (wf / "ci.yml").write_text("jobs:\n  x:\n    steps:\n      - run: semgrep --version\n", encoding="utf-8")
    monkeypatch.setattr(workflow_deprecated_invocation_gate, "ROOT", repo)
    monkeypatch.setattr(workflow_deprecated_invocation_gate, "evidence_root", lambda: repo / "evidence")
    assert workflow_deprecated_invocation_gate.main([]) == 0


def test_workflow_deprecated_invocation_gate_fails_on_python_module_semgrep(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True)
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    (wf / "ci.yml").write_text("jobs:\n  x:\n    steps:\n      - run: python -m semgrep --version\n", encoding="utf-8")
    monkeypatch.setattr(workflow_deprecated_invocation_gate, "ROOT", repo)
    monkeypatch.setattr(workflow_deprecated_invocation_gate, "evidence_root", lambda: repo / "evidence")
    assert workflow_deprecated_invocation_gate.main([]) == 1
    report = json.loads((ev / "workflow_deprecated_invocation_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(item.startswith("deprecated_invocation:") for item in report["findings"])
