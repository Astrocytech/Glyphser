from __future__ import annotations

import json
from pathlib import Path

from tooling.security import workflow_policy_coverage_gate


def test_workflow_policy_coverage_report_is_reproducible_with_fixed_epoch(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "ci.yml").write_text("jobs:\n  test:\n    runs-on: ubuntu-latest\n", encoding="utf-8")
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "workflow_policy_coverage.json").write_text(
        json.dumps({"workflows": ["ci.yml"]}) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(workflow_policy_coverage_gate, "ROOT", repo)
    monkeypatch.setattr(
        workflow_policy_coverage_gate,
        "POLICY_PATH",
        repo / "governance" / "security" / "workflow_policy_coverage.json",
    )
    monkeypatch.setattr(workflow_policy_coverage_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "1700000000")
    monkeypatch.setenv("TZ", "UTC")
    monkeypatch.setenv("LC_ALL", "C.UTF-8")
    monkeypatch.setenv("LANG", "C.UTF-8")

    assert workflow_policy_coverage_gate.main([]) == 0
    out = repo / "evidence" / "security" / "workflow_policy_coverage_gate.json"
    first = out.read_bytes()

    assert workflow_policy_coverage_gate.main([]) == 0
    second = out.read_bytes()

    assert first == second
