from __future__ import annotations

import json
from pathlib import Path

from tooling.security import recurring_failure_closure_gate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_recurring_failure_closure_gate_passes_after_required_green_runs(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"

    _write_json(
        repo / "evidence" / "security" / "ci_failure_classifier_history.json",
        {
            "schema_version": 1,
            "runs": [
                {
                    "run_id": "1",
                    "timestamp_utc": "2026-03-01T00:00:00+00:00",
                    "issues": ["security_super_gate.json:timeout"],
                },
                {"run_id": "2", "timestamp_utc": "2026-03-02T00:00:00+00:00", "issues": []},
                {"run_id": "3", "timestamp_utc": "2026-03-03T00:00:00+00:00", "issues": []},
                {"run_id": "4", "timestamp_utc": "2026-03-04T00:00:00+00:00", "issues": []},
            ],
        },
    )
    _write_json(
        repo / "governance" / "security" / "ci_failure_closure_requests.json",
        {
            "schema_version": 1,
            "required_green_runs": 3,
            "requested_resolutions": ["security_super_gate.json:timeout"],
        },
    )

    monkeypatch.setattr(recurring_failure_closure_gate, "ROOT", repo)
    monkeypatch.setattr(
        recurring_failure_closure_gate,
        "HISTORY_PATH",
        repo / "evidence" / "security" / "ci_failure_classifier_history.json",
    )
    monkeypatch.setattr(
        recurring_failure_closure_gate,
        "CLOSURE_REQUESTS",
        repo / "governance" / "security" / "ci_failure_closure_requests.json",
    )
    monkeypatch.setattr(recurring_failure_closure_gate, "evidence_root", lambda: ev)

    assert recurring_failure_closure_gate.main([]) == 0
    report = json.loads((ev / "security" / "recurring_failure_closure_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["verification"]["verified"] == ["security_super_gate.json:timeout"]


def test_recurring_failure_closure_gate_fails_when_not_green_long_enough(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"

    _write_json(
        repo / "evidence" / "security" / "ci_failure_classifier_history.json",
        {
            "schema_version": 1,
            "runs": [
                {
                    "run_id": "1",
                    "timestamp_utc": "2026-03-01T00:00:00+00:00",
                    "issues": ["security_super_gate.json:timeout"],
                },
                {"run_id": "2", "timestamp_utc": "2026-03-02T00:00:00+00:00", "issues": []},
            ],
        },
    )
    _write_json(
        repo / "governance" / "security" / "ci_failure_closure_requests.json",
        {
            "schema_version": 1,
            "required_green_runs": 3,
            "requested_resolutions": ["security_super_gate.json:timeout"],
        },
    )

    monkeypatch.setattr(recurring_failure_closure_gate, "ROOT", repo)
    monkeypatch.setattr(
        recurring_failure_closure_gate,
        "HISTORY_PATH",
        repo / "evidence" / "security" / "ci_failure_classifier_history.json",
    )
    monkeypatch.setattr(
        recurring_failure_closure_gate,
        "CLOSURE_REQUESTS",
        repo / "governance" / "security" / "ci_failure_closure_requests.json",
    )
    monkeypatch.setattr(recurring_failure_closure_gate, "evidence_root", lambda: ev)

    assert recurring_failure_closure_gate.main([]) == 1
    report = json.loads((ev / "security" / "recurring_failure_closure_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(item.startswith("closure_insufficient_green_runs:security_super_gate.json:timeout") for item in report["findings"])
