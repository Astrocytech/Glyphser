from __future__ import annotations

import json
from pathlib import Path

from tooling.security import monthly_top_recurring_failures_report


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_monthly_top_recurring_failures_report_includes_owner_and_eta(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"

    _write_json(
        repo / "evidence" / "security" / "ci_failure_classifier_history.json",
        {
            "schema_version": 1,
            "counts": {
                "security_super_gate.json:missing_env:TZ": 3,
                "workflow_risky_patterns_gate.json:unsafe_shell_expansion": 2,
            },
            "runs": [
                {
                    "run_id": "100",
                    "timestamp_utc": "2026-03-01T00:00:00+00:00",
                    "issues": ["security_super_gate.json:missing_env:TZ"],
                },
                {
                    "run_id": "101",
                    "timestamp_utc": "2026-03-02T00:00:00+00:00",
                    "issues": [
                        "security_super_gate.json:missing_env:TZ",
                        "workflow_risky_patterns_gate.json:unsafe_shell_expansion",
                    ],
                },
            ],
        },
    )
    _write_json(
        repo / "governance" / "security" / "ci_failure_owner_map.json",
        {
            "schema_version": 1,
            "default_owner": "security-platform",
            "default_eta_days": 30,
            "issue_overrides": {},
            "report_owner_overrides": {
                "security_super_gate.json": {
                    "owner": "security-platform",
                    "action": "Fix prereq stability.",
                    "eta_days": 14,
                }
            },
        },
    )

    monkeypatch.setattr(monthly_top_recurring_failures_report, "ROOT", repo)
    monkeypatch.setattr(
        monthly_top_recurring_failures_report,
        "PERSISTENT_HISTORY",
        repo / "evidence" / "security" / "ci_failure_classifier_history.json",
    )
    monkeypatch.setattr(
        monthly_top_recurring_failures_report,
        "OWNER_MAP_PATH",
        repo / "governance" / "security" / "ci_failure_owner_map.json",
    )
    monkeypatch.setattr(monthly_top_recurring_failures_report, "evidence_root", lambda: ev)

    assert monthly_top_recurring_failures_report.main([]) == 0

    report = json.loads((ev / "security" / "monthly_top_recurring_failures_report.json").read_text(encoding="utf-8"))
    assert report["status"] == "WARN"
    assert report["summary"]["total_recurring_issues"] == 2
    top = report["top_recurring_failures"]
    assert top
    assert all(item.get("owner") for item in top)
    assert all(item.get("action") for item in top)
    assert all(item.get("action_eta_utc") for item in top)


def test_monthly_top_recurring_failures_report_passes_with_no_recurring(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"

    _write_json(
        repo / "evidence" / "security" / "ci_failure_classifier_history.json",
        {
            "schema_version": 1,
            "counts": {"security_super_gate.json:missing_env:TZ": 1},
            "runs": [],
        },
    )
    _write_json(
        repo / "governance" / "security" / "ci_failure_owner_map.json",
        {"schema_version": 1, "default_owner": "security-platform", "default_eta_days": 30},
    )

    monkeypatch.setattr(monthly_top_recurring_failures_report, "ROOT", repo)
    monkeypatch.setattr(
        monthly_top_recurring_failures_report,
        "PERSISTENT_HISTORY",
        repo / "evidence" / "security" / "ci_failure_classifier_history.json",
    )
    monkeypatch.setattr(
        monthly_top_recurring_failures_report,
        "OWNER_MAP_PATH",
        repo / "governance" / "security" / "ci_failure_owner_map.json",
    )
    monkeypatch.setattr(monthly_top_recurring_failures_report, "evidence_root", lambda: ev)

    assert monthly_top_recurring_failures_report.main([]) == 0
    report = json.loads((ev / "security" / "monthly_top_recurring_failures_report.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["top_recurring_failures"] == []
