from __future__ import annotations

import json
from pathlib import Path

from tooling.security import scheduled_workflow_backpressure_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    _write(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def test_scheduled_workflow_backpressure_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(
        repo / ".github" / "workflows" / "security-maintenance.yml",
        "on:\n  schedule:\n    - cron: '0 0 * * *'\nconcurrency:\n  group: ${{ github.workflow }}-${{ github.ref }}\n  cancel-in-progress: false\n",
    )
    _write_json(
        repo / "governance" / "security" / "scheduled_workflow_backpressure_policy.json",
        {
            "scheduled_hardening_workflows": [".github/workflows/security-maintenance.yml"],
            "required_concurrency": {"group_must_contain": "${{ github.workflow }}", "cancel_in_progress": False},
        },
    )

    monkeypatch.setattr(scheduled_workflow_backpressure_gate, "ROOT", repo)
    monkeypatch.setattr(
        scheduled_workflow_backpressure_gate,
        "POLICY",
        repo / "governance" / "security" / "scheduled_workflow_backpressure_policy.json",
    )
    monkeypatch.setattr(scheduled_workflow_backpressure_gate, "evidence_root", lambda: repo / "evidence")
    assert scheduled_workflow_backpressure_gate.main([]) == 0


def test_scheduled_workflow_backpressure_gate_fails_missing_concurrency(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(repo / ".github" / "workflows" / "security-maintenance.yml", "on:\n  schedule:\n    - cron: '0 0 * * *'\n")
    _write_json(
        repo / "governance" / "security" / "scheduled_workflow_backpressure_policy.json",
        {
            "scheduled_hardening_workflows": [".github/workflows/security-maintenance.yml"],
            "required_concurrency": {"group_must_contain": "${{ github.workflow }}", "cancel_in_progress": False},
        },
    )

    monkeypatch.setattr(scheduled_workflow_backpressure_gate, "ROOT", repo)
    monkeypatch.setattr(
        scheduled_workflow_backpressure_gate,
        "POLICY",
        repo / "governance" / "security" / "scheduled_workflow_backpressure_policy.json",
    )
    monkeypatch.setattr(scheduled_workflow_backpressure_gate, "evidence_root", lambda: repo / "evidence")
    assert scheduled_workflow_backpressure_gate.main([]) == 1
