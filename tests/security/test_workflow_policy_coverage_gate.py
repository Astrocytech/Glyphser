from __future__ import annotations

import json
from pathlib import Path

from tooling.security import workflow_policy_coverage_gate


def test_workflow_policy_coverage_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True)
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    gov = repo / "governance" / "security"
    gov.mkdir(parents=True)
    (wf / "a.yml").write_text("name: a\n", encoding="utf-8")
    (gov / "workflow_policy_coverage.json").write_text(
        json.dumps({"workflows": ["a.yml"]}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(workflow_policy_coverage_gate, "ROOT", repo)
    monkeypatch.setattr(workflow_policy_coverage_gate, "POLICY_PATH", gov / "workflow_policy_coverage.json")
    monkeypatch.setattr(workflow_policy_coverage_gate, "evidence_root", lambda: repo / "evidence")
    assert workflow_policy_coverage_gate.main([]) == 0


def test_workflow_policy_coverage_gate_fails_on_orphan(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True)
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    gov = repo / "governance" / "security"
    gov.mkdir(parents=True)
    (wf / "a.yml").write_text("name: a\n", encoding="utf-8")
    (wf / "b.yml").write_text("name: b\n", encoding="utf-8")
    (gov / "workflow_policy_coverage.json").write_text(
        json.dumps({"workflows": ["a.yml"]}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(workflow_policy_coverage_gate, "ROOT", repo)
    monkeypatch.setattr(workflow_policy_coverage_gate, "POLICY_PATH", gov / "workflow_policy_coverage.json")
    monkeypatch.setattr(workflow_policy_coverage_gate, "evidence_root", lambda: repo / "evidence")
    assert workflow_policy_coverage_gate.main([]) == 1
    report = json.loads((ev / "workflow_policy_coverage_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(item.startswith("workflow_not_covered_by_policy:b.yml") for item in report["findings"])
