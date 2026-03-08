from __future__ import annotations

import json
from pathlib import Path

from tooling.security import ci_incident_replay_harness


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_ci_incident_replay_harness_passes_on_expected_fixture(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    fixture = repo / "fixtures.json"
    _write_json(
        fixture,
        {
            "incidents": [
                {"id": "a", "log_excerpt": "No module named pip_audit", "expected_reason": "pip_audit_execution_failed"},
                {"id": "b", "log_excerpt": "security-events: write", "expected_reason": "security_events_permission_missing"},
            ]
        },
    )
    monkeypatch.setattr(ci_incident_replay_harness, "ROOT", repo)
    monkeypatch.setattr(ci_incident_replay_harness, "evidence_root", lambda: repo / "evidence")
    assert ci_incident_replay_harness.main(["--fixture", str(fixture)]) == 0


def test_ci_incident_replay_harness_fails_on_mismatch(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    fixture = repo / "fixtures.json"
    _write_json(
        fixture,
        {"incidents": [{"id": "x", "log_excerpt": "No module named pip_audit", "expected_reason": "wrong"}]},
    )
    monkeypatch.setattr(ci_incident_replay_harness, "ROOT", repo)
    monkeypatch.setattr(ci_incident_replay_harness, "evidence_root", lambda: repo / "evidence")
    assert ci_incident_replay_harness.main(["--fixture", str(fixture)]) == 1
    report = json.loads((repo / "evidence" / "security" / "ci_incident_replay_harness.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(str(item).startswith("incident_mismatch:") for item in report["findings"])
