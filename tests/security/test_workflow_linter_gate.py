from __future__ import annotations

import json
from pathlib import Path

from tooling.security import workflow_linter_gate


def _write_report(path: Path, status: str) -> None:
    path.write_text(json.dumps({"status": status, "findings": []}) + "\n", encoding="utf-8")


def test_workflow_linter_gate_passes_when_dependencies_pass(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    for name in workflow_linter_gate.DEPENDENT_REPORTS:
        _write_report(sec / name, "PASS")
    monkeypatch.setattr(workflow_linter_gate, "evidence_root", lambda: repo / "evidence")
    assert workflow_linter_gate.main([]) == 0


def test_workflow_linter_gate_fails_on_missing_or_failed_dependency(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    _write_report(sec / "workflow_risky_patterns_gate.json", "PASS")
    _write_report(sec / "workflow_pinning.json", "FAIL")
    monkeypatch.setattr(workflow_linter_gate, "evidence_root", lambda: repo / "evidence")
    assert workflow_linter_gate.main([]) == 1
    payload = json.loads((sec / "workflow_linter_gate.json").read_text(encoding="utf-8"))
    assert payload["status"] == "FAIL"
    assert any(str(item).startswith("dependency_report_not_pass:") for item in payload["findings"])
    assert any(str(item).startswith("missing_dependency_report:") for item in payload["findings"])


def test_workflow_linter_gate_fails_on_yaml_rule_violation(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    for name in workflow_linter_gate.DEPENDENT_REPORTS:
        _write_report(sec / name, "PASS")

    workflows = repo / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "ci.yml").write_text(
        "name: ci\njobs:\n  build:\n    steps:\n      - uses: actions/checkout@main\n",
        encoding="utf-8",
    )
    rule_pack = repo / "tooling" / "security" / "workflow_yaml_lint_rules.json"
    rule_pack.parent.mkdir(parents=True, exist_ok=True)
    rule_pack.write_text(
        json.dumps({"rules": [{"id": "WF-TEST-001", "pattern": "@main\\s*$"}]}, indent=2) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(workflow_linter_gate, "ROOT", repo)
    monkeypatch.setattr(workflow_linter_gate, "WORKFLOWS_DIR", workflows)
    monkeypatch.setattr(workflow_linter_gate, "RULE_PACK", rule_pack)
    monkeypatch.setattr(workflow_linter_gate, "evidence_root", lambda: repo / "evidence")
    assert workflow_linter_gate.main([]) == 1
    payload = json.loads((sec / "workflow_linter_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("lint_rule_violation:WF-TEST-001:") for item in payload["findings"])
