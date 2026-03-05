from __future__ import annotations

import json
from pathlib import Path

from tooling.security import workflow_retrofit_process_gate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_workflow_retrofit_process_gate_passes_when_controls_present(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    ev = repo / "evidence"
    control = "python tooling/security/security_super_gate.py --strict-key"
    _write_json(
        repo / "governance" / "security" / "workflow_retrofit_policy.json",
        {"mandatory_workflows": [".github/workflows/ci.yml"], "required_controls": [control]},
    )
    _write_text(repo / ".github" / "workflows" / "ci.yml", f"jobs:\n  x:\n    steps:\n      - run: {control}\n")
    monkeypatch.setattr(workflow_retrofit_process_gate, "ROOT", repo)
    monkeypatch.setattr(
        workflow_retrofit_process_gate, "POLICY", repo / "governance" / "security" / "workflow_retrofit_policy.json"
    )
    monkeypatch.setattr(workflow_retrofit_process_gate, "evidence_root", lambda: ev)
    assert workflow_retrofit_process_gate.main([]) == 0


def test_workflow_retrofit_process_gate_fails_when_controls_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    ev = repo / "evidence"
    control = "python tooling/security/security_super_gate.py --strict-key"
    _write_json(
        repo / "governance" / "security" / "workflow_retrofit_policy.json",
        {"mandatory_workflows": [".github/workflows/ci.yml"], "required_controls": [control]},
    )
    _write_text(repo / ".github" / "workflows" / "ci.yml", "jobs:\n")
    monkeypatch.setattr(workflow_retrofit_process_gate, "ROOT", repo)
    monkeypatch.setattr(
        workflow_retrofit_process_gate, "POLICY", repo / "governance" / "security" / "workflow_retrofit_policy.json"
    )
    monkeypatch.setattr(workflow_retrofit_process_gate, "evidence_root", lambda: ev)
    assert workflow_retrofit_process_gate.main([]) == 1
    report = json.loads((ev / "security" / "workflow_retrofit_process_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("missing_retrofit_control:.github/workflows/ci.yml:") for item in report["findings"])
