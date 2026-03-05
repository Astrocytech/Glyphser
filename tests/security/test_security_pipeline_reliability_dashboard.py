from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_pipeline_reliability_dashboard


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_security_pipeline_reliability_dashboard_updates_mttr_and_flake(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"

    _write_json(
        ev / "security" / "security_super_gate.json",
        {
            "results": [
                {"cmd": ["python", "tooling/security/gate_a.py"], "status": "FAIL"},
            ]
        },
    )
    _write_json(
        repo / "evidence" / "security" / "security_pipeline_reliability_history.json",
        {
            "schema_version": 1,
            "runs": [
                {"run_id": "1", "failed_gates": ["tooling/security/gate_a.py"]},
                {"run_id": "2", "failed_gates": []},
            ],
        },
    )
    _write_json(
        repo / "governance" / "security" / "security_workflow_reliability_budget_policy.json",
        {"flake_budget_events": 8, "max_open_gate_failures": 5},
    )

    monkeypatch.setattr(security_pipeline_reliability_dashboard, "ROOT", repo)
    monkeypatch.setattr(
        security_pipeline_reliability_dashboard,
        "HISTORY",
        repo / "evidence" / "security" / "security_pipeline_reliability_history.json",
    )
    monkeypatch.setattr(
        security_pipeline_reliability_dashboard,
        "POLICY",
        repo / "governance" / "security" / "security_workflow_reliability_budget_policy.json",
    )
    monkeypatch.setattr(security_pipeline_reliability_dashboard, "evidence_root", lambda: ev)

    assert security_pipeline_reliability_dashboard.main([]) == 0
    report = json.loads((ev / "security" / "security_pipeline_reliability_dashboard.json").read_text(encoding="utf-8"))
    assert report["summary"]["runs_tracked"] == 3
    assert "mttr_runs" in report["summary"]
    assert "flake_rate" in report["summary"]
    assert report["summary"]["flake_budget_events"] == 8
    assert "flake_budget_burn_down_pct" in report["summary"]


def test_security_pipeline_reliability_dashboard_warns_when_super_gate_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"

    monkeypatch.setattr(security_pipeline_reliability_dashboard, "ROOT", repo)
    monkeypatch.setattr(
        security_pipeline_reliability_dashboard,
        "HISTORY",
        repo / "evidence" / "security" / "security_pipeline_reliability_history.json",
    )
    monkeypatch.setattr(security_pipeline_reliability_dashboard, "evidence_root", lambda: ev)

    assert security_pipeline_reliability_dashboard.main([]) == 0
    report = json.loads((ev / "security" / "security_pipeline_reliability_dashboard.json").read_text(encoding="utf-8"))
    assert report["status"] == "WARN"
    assert "missing_security_super_gate_report" in report["findings"]


def test_security_pipeline_reliability_dashboard_warns_when_budget_exceeded(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    _write_json(
        ev / "security" / "security_super_gate.json",
        {
            "results": [
                {"cmd": ["python", "tooling/security/gate_a.py"], "status": "FAIL"},
            ]
        },
    )
    _write_json(
        repo / "evidence" / "security" / "security_pipeline_reliability_history.json",
        {
            "schema_version": 1,
            "runs": [
                {"run_id": "1", "failed_gates": ["tooling/security/gate_a.py"]},
                {"run_id": "2", "failed_gates": []},
                {"run_id": "3", "failed_gates": ["tooling/security/gate_a.py"]},
                {"run_id": "4", "failed_gates": []},
                {"run_id": "5", "failed_gates": ["tooling/security/gate_a.py"]},
                {"run_id": "6", "failed_gates": []},
            ],
        },
    )
    _write_json(
        repo / "governance" / "security" / "security_workflow_reliability_budget_policy.json",
        {"flake_budget_events": 1, "max_open_gate_failures": 5},
    )

    monkeypatch.setattr(security_pipeline_reliability_dashboard, "ROOT", repo)
    monkeypatch.setattr(
        security_pipeline_reliability_dashboard,
        "HISTORY",
        repo / "evidence" / "security" / "security_pipeline_reliability_history.json",
    )
    monkeypatch.setattr(
        security_pipeline_reliability_dashboard,
        "POLICY",
        repo / "governance" / "security" / "security_workflow_reliability_budget_policy.json",
    )
    monkeypatch.setattr(security_pipeline_reliability_dashboard, "evidence_root", lambda: ev)

    assert security_pipeline_reliability_dashboard.main([]) == 0
    report = json.loads((ev / "security" / "security_pipeline_reliability_dashboard.json").read_text(encoding="utf-8"))
    assert report["status"] == "WARN"
    assert any(str(item).startswith("flake_budget_exceeded:") for item in report["findings"])
