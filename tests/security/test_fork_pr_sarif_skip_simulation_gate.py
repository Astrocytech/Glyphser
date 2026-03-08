from __future__ import annotations

import json
from pathlib import Path

from tooling.security import fork_pr_sarif_skip_simulation_gate


def test_fork_pr_sarif_skip_simulation_gate_passes_when_ci_has_required_markers(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    wf = repo / ".github" / "workflows" / "ci.yml"
    wf.parent.mkdir(parents=True, exist_ok=True)
    wf.write_text(
        "\n".join(
            [
                "name: ci",
                "if: github.event_name == 'push'",
                "Upload SARIF to Code Scanning",
                "Upload security artifacts",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(fork_pr_sarif_skip_simulation_gate, "ROOT", repo)
    monkeypatch.setattr(fork_pr_sarif_skip_simulation_gate, "CI_WORKFLOW", wf)
    monkeypatch.setattr(fork_pr_sarif_skip_simulation_gate, "evidence_root", lambda: repo / "evidence")
    assert fork_pr_sarif_skip_simulation_gate.main([]) == 0


def test_fork_pr_sarif_skip_simulation_gate_fails_when_markers_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    wf = repo / ".github" / "workflows" / "ci.yml"
    wf.parent.mkdir(parents=True, exist_ok=True)
    wf.write_text("name: ci\n", encoding="utf-8")

    monkeypatch.setattr(fork_pr_sarif_skip_simulation_gate, "ROOT", repo)
    monkeypatch.setattr(fork_pr_sarif_skip_simulation_gate, "CI_WORKFLOW", wf)
    monkeypatch.setattr(fork_pr_sarif_skip_simulation_gate, "evidence_root", lambda: repo / "evidence")
    assert fork_pr_sarif_skip_simulation_gate.main([]) == 1
    report = json.loads(
        (repo / "evidence" / "security" / "fork_pr_sarif_skip_simulation_gate.json").read_text(encoding="utf-8")
    )
    assert "missing_fork_pr_sarif_skip_condition" in report["findings"]
