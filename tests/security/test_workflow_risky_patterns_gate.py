from __future__ import annotations

import json
from pathlib import Path

from tooling.security import workflow_risky_patterns_gate


def test_workflow_risky_patterns_gate_passes_for_pinned_actions(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True)
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    (wf / "ci.yml").write_text(
        "jobs:\n  x:\n    steps:\n      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(workflow_risky_patterns_gate, "ROOT", repo)
    monkeypatch.setattr(workflow_risky_patterns_gate, "evidence_root", lambda: repo / "evidence")
    assert workflow_risky_patterns_gate.main([]) == 0


def test_workflow_risky_patterns_gate_fails_for_unsafe_patterns(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True)
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    (wf / "ci.yml").write_text(
        "\n".join(
            [
                "permissions: write-all",
                "jobs:",
                "  x:",
                "    steps:",
                "      - uses: actions/checkout@v4",
                "      - run: echo ${{ github.event.pull_request.title }}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(workflow_risky_patterns_gate, "ROOT", repo)
    monkeypatch.setattr(workflow_risky_patterns_gate, "evidence_root", lambda: repo / "evidence")
    assert workflow_risky_patterns_gate.main([]) == 1
    report = json.loads((ev / "workflow_risky_patterns_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(item.startswith("forbidden_permission_write_all:") for item in report["findings"])
    assert any(item.startswith("unpinned_action_ref:") for item in report["findings"])
    assert any(item.startswith("untrusted_pr_expr_in_run:") for item in report["findings"])
