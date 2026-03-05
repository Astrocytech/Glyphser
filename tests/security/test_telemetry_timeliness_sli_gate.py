from __future__ import annotations

import json
from pathlib import Path

from tooling.security import telemetry_timeliness_sli_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    _write(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def test_telemetry_timeliness_sli_gate_passes_with_fresh_reports(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_json(
        repo / "governance" / "security" / "security_observability_policy.json",
        {
            "telemetry_timeliness": {
                "required_reports": [
                    "security_event_export.json",
                    "security_event_schema_gate.json",
                    "telemetry_completeness_sli_gate.json",
                ],
                "max_report_age_minutes": 15,
                "timely_reports_rate_threshold": 1.0,
                "allowed_future_skew_minutes": 1,
            }
        },
    )
    for name in [
        "security_event_export.json",
        "security_event_schema_gate.json",
        "telemetry_completeness_sli_gate.json",
    ]:
        _write_json(
            repo / "evidence" / "security" / name,
            {
                "status": "PASS",
                "findings": [],
                "summary": {},
                "metadata": {"generated_at_utc": "2026-03-05T12:00:00+00:00"},
            },
        )

    monkeypatch.setattr(telemetry_timeliness_sli_gate, "ROOT", repo)
    monkeypatch.setattr(
        telemetry_timeliness_sli_gate,
        "POLICY",
        repo / "governance/security/security_observability_policy.json",
    )
    monkeypatch.setattr(telemetry_timeliness_sli_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_FIXED_UTC", "2026-03-05T12:10:00+00:00")
    assert telemetry_timeliness_sli_gate.main([]) == 0


def test_telemetry_timeliness_sli_gate_fails_on_stale_report(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_json(
        repo / "governance" / "security" / "security_observability_policy.json",
        {
            "telemetry_timeliness": {
                "required_reports": ["security_event_export.json", "security_event_schema_gate.json"],
                "max_report_age_minutes": 15,
                "timely_reports_rate_threshold": 1.0,
            }
        },
    )
    _write_json(
        repo / "evidence" / "security" / "security_event_export.json",
        {
            "status": "PASS",
            "findings": [],
            "summary": {},
            "metadata": {"generated_at_utc": "2026-03-05T11:00:00+00:00"},
        },
    )
    _write_json(
        repo / "evidence" / "security" / "security_event_schema_gate.json",
        {
            "status": "PASS",
            "findings": [],
            "summary": {},
            "metadata": {"generated_at_utc": "2026-03-05T11:59:00+00:00"},
        },
    )

    monkeypatch.setattr(telemetry_timeliness_sli_gate, "ROOT", repo)
    monkeypatch.setattr(
        telemetry_timeliness_sli_gate,
        "POLICY",
        repo / "governance/security/security_observability_policy.json",
    )
    monkeypatch.setattr(telemetry_timeliness_sli_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_FIXED_UTC", "2026-03-05T12:00:00+00:00")
    assert telemetry_timeliness_sli_gate.main([]) == 1

    report = json.loads((repo / "evidence" / "security" / "telemetry_timeliness_sli_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(item.startswith("report_stale:security_event_export.json:") for item in report["findings"])
    assert any(item.startswith("telemetry_timeliness_below_threshold:") for item in report["findings"])
