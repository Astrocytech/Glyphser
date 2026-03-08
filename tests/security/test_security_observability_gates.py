from __future__ import annotations

import json
from pathlib import Path

from tooling.security import (
    security_dashboard_export,
    security_schema_normalization_gate,
    security_slo_report,
    security_trend_gate,
)


def test_security_slo_trend_dashboard(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    for name in [
        "policy_signature.json",
        "provenance_signature.json",
        "evidence_attestation_gate.json",
        "security_super_gate.json",
    ]:
        (sec / name).write_text('{"status":"PASS","findings":[],"summary":{},"metadata":{}}\n', encoding="utf-8")
    monkeypatch.setattr(security_slo_report, "ROOT", repo)
    monkeypatch.setattr(security_slo_report, "evidence_root", lambda: repo / "evidence")
    assert security_slo_report.main([]) == 0
    monkeypatch.setattr(security_trend_gate, "ROOT", repo)
    monkeypatch.setattr(security_trend_gate, "evidence_root", lambda: repo / "evidence")
    assert security_trend_gate.main([]) == 0
    assert (sec / "security_trend_alert.json").exists()
    monkeypatch.setattr(security_dashboard_export, "ROOT", repo)
    monkeypatch.setattr(security_dashboard_export, "evidence_root", lambda: repo / "evidence")
    assert security_dashboard_export.main([]) == 0
    dashboard = json.loads((sec / "security_dashboard.json").read_text(encoding="utf-8"))
    assert dashboard["metadata"]["api_contract_version"] == "v1"
    assert "control_coverage_ratio" in dashboard["summary"]["kpis"]
    assert "mean_hardening_lead_time_hours" in dashboard["summary"]["kpis"]
    assert dashboard["summary"]["kpis"]["mean_hardening_lead_time_hours"] == 0.0
    assert dashboard["summary"]["kpis"]["false_positive_rate_per_gate"] == {}
    assert dashboard["summary"]["kpis"]["active_bypass_exception_volume_total"] == 0
    monkeypatch.setattr(security_schema_normalization_gate, "ROOT", repo)
    monkeypatch.setattr(security_schema_normalization_gate, "evidence_root", lambda: repo / "evidence")
    assert security_schema_normalization_gate.main([]) == 0


def test_security_dashboard_export_computes_mean_hardening_lead_time(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    gov = repo / "governance" / "security"
    sec.mkdir(parents=True)
    gov.mkdir(parents=True)
    for name in [
        "policy_signature.json",
        "provenance_signature.json",
        "evidence_attestation_gate.json",
        "security_slo_report.json",
    ]:
        (sec / name).write_text('{"status":"PASS","findings":[],"summary":{},"metadata":{}}\n', encoding="utf-8")
    (gov / "hardening_issue_enforcement_timeline.json").write_text(
        json.dumps(
            {
                "events": [
                    {
                        "issue_id": "SEC-1",
                        "issue_identified_at_utc": "2026-03-01T00:00:00+00:00",
                        "enforced_in_ci_at_utc": "2026-03-01T12:00:00+00:00",
                    },
                    {
                        "issue_id": "SEC-2",
                        "issue_identified_at_utc": "2026-03-02T00:00:00+00:00",
                        "enforced_in_ci_at_utc": "2026-03-03T00:00:00+00:00",
                    },
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(security_dashboard_export, "ROOT", repo)
    monkeypatch.setattr(security_dashboard_export, "evidence_root", lambda: repo / "evidence")
    assert security_dashboard_export.main([]) == 0
    dashboard = json.loads((sec / "security_dashboard.json").read_text(encoding="utf-8"))
    kpis = dashboard["summary"]["kpis"]
    assert kpis["hardening_lead_time_samples"] == 2
    assert kpis["hardening_lead_time_complete_records"] == 2
    assert kpis["hardening_lead_time_invalid_records"] == 0
    assert kpis["mean_hardening_lead_time_hours"] == 18.0


def test_security_dashboard_export_computes_false_positive_rate_per_gate(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    gov = repo / "governance" / "security"
    sec.mkdir(parents=True)
    gov.mkdir(parents=True)
    for name in [
        "policy_signature.json",
        "provenance_signature.json",
        "evidence_attestation_gate.json",
        "security_slo_report.json",
    ]:
        (sec / name).write_text('{"status":"PASS","findings":[],"summary":{},"metadata":{}}\n', encoding="utf-8")
    (gov / "security_gate_false_positive_log.json").write_text(
        json.dumps(
            {
                "events": [
                    {"gate": "semgrep_gate", "classification": "false_positive"},
                    {"gate": "semgrep_gate", "classification": "true_positive"},
                    {"gate": "bandit_gate", "classification": "true_positive"},
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(security_dashboard_export, "ROOT", repo)
    monkeypatch.setattr(security_dashboard_export, "evidence_root", lambda: repo / "evidence")
    assert security_dashboard_export.main([]) == 0
    dashboard = json.loads((sec / "security_dashboard.json").read_text(encoding="utf-8"))
    kpis = dashboard["summary"]["kpis"]
    assert kpis["false_positive_rate_per_gate"]["semgrep_gate"] == 0.5
    assert kpis["false_positive_rate_per_gate"]["bandit_gate"] == 0.0
    assert kpis["false_positive_reviewed_findings"] == 3
    assert kpis["false_positive_records_invalid"] == 0
    assert kpis["false_positive_rate_overall"] == 0.3333


def test_security_dashboard_export_computes_bypass_exception_volume_and_aging(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    gov = repo / "governance" / "security"
    repro = repo / "evidence" / "repro"
    sec.mkdir(parents=True)
    gov.mkdir(parents=True)
    repro.mkdir(parents=True)
    for name in [
        "policy_signature.json",
        "provenance_signature.json",
        "evidence_attestation_gate.json",
        "security_slo_report.json",
    ]:
        (sec / name).write_text('{"status":"PASS","findings":[],"summary":{},"metadata":{}}\n', encoding="utf-8")
    (gov / "temporary_exceptions.json").write_text(
        json.dumps(
            {
                "exceptions": [
                    {
                        "id": "ex-1",
                        "created_at_utc": "2026-03-01T00:00:00+00:00",
                        "expires_at_utc": "2026-03-20T00:00:00+00:00",
                    }
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (gov / "temporary_waiver_policy.json").write_text(
        json.dumps({"waiver_file_glob": "evidence/repro/waivers.json"}) + "\n",
        encoding="utf-8",
    )
    (repro / "waivers.json").write_text(
        json.dumps(
            {
                "waivers": [
                    {
                        "id": "w-1",
                        "created_at_utc": "2026-03-05T00:00:00+00:00",
                        "expires_at_utc": "2026-03-08T00:00:00+00:00",
                    }
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("GLYPHSER_FIXED_UTC", "2026-03-06T00:00:00+00:00")
    monkeypatch.setattr(security_dashboard_export, "ROOT", repo)
    monkeypatch.setattr(security_dashboard_export, "evidence_root", lambda: repo / "evidence")
    assert security_dashboard_export.main([]) == 0
    dashboard = json.loads((sec / "security_dashboard.json").read_text(encoding="utf-8"))
    kpis = dashboard["summary"]["kpis"]
    assert kpis["active_exception_volume"] == 1
    assert kpis["active_waiver_volume"] == 1
    assert kpis["active_bypass_exception_volume_total"] == 2
    assert kpis["bypass_exception_aging_records"] == 2
    assert kpis["bypass_exception_aging_invalid_records"] == 0
    assert kpis["bypass_exception_aging_mean_days"] == 3.0
    assert kpis["bypass_exception_aging_max_days"] == 5.0
    assert kpis["bypass_exception_nearing_expiry_7d"] == 1


def test_security_trend_gate_emits_remediation_alert(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    for name, status in [
        ("policy_signature.json", "PASS"),
        ("provenance_signature.json", "FAIL"),
        ("evidence_attestation_gate.json", "PASS"),
        ("security_super_gate.json", "FAIL"),
    ]:
        (sec / name).write_text(
            json.dumps({"status": status, "findings": [], "summary": {}, "metadata": {}}) + "\n",
            encoding="utf-8",
        )
    (sec / "security_slo_history.json").write_text(json.dumps({"values": [1.0]}) + "\n", encoding="utf-8")
    monkeypatch.setattr(security_slo_report, "ROOT", repo)
    monkeypatch.setattr(security_slo_report, "evidence_root", lambda: repo / "evidence")
    assert security_slo_report.main([]) == 1

    monkeypatch.setattr(security_trend_gate, "ROOT", repo)
    monkeypatch.setattr(security_trend_gate, "evidence_root", lambda: repo / "evidence")
    assert security_trend_gate.main([]) == 1
    alert = json.loads((sec / "security_trend_alert.json").read_text(encoding="utf-8"))
    assert alert["status"] == "ALERT"
    assert alert["summary"]["alerts"]
    first = alert["summary"]["alerts"][0]
    assert first["code"] == "security_trend_degrading"
    assert first["suggested_actions"]


def test_security_trend_gate_emits_burn_rate_alert(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "security_observability_policy.json").write_text(
        json.dumps({"slo_target": 0.99, "burn_rate_alert_threshold": 1.0}) + "\n",
        encoding="utf-8",
    )
    (sec / "security_slo_report.json").write_text(
        json.dumps(
            {
                "status": "FAIL",
                "findings": [],
                "summary": {"pass_rate": 0.5, "burn_rate": 50.0},
                "metadata": {},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (sec / "security_slo_history.json").write_text(json.dumps({"values": [0.5]}) + "\n", encoding="utf-8")
    for required in ["security_super_gate.json", "policy_signature.json", "provenance_signature.json"]:
        (sec / required).write_text('{"status":"PASS","findings":[],"summary":{},"metadata":{}}\n', encoding="utf-8")
    monkeypatch.setattr(security_trend_gate, "ROOT", repo)
    monkeypatch.setattr(security_trend_gate, "evidence_root", lambda: repo / "evidence")
    assert security_trend_gate.main([]) == 1
    alert = json.loads((sec / "security_trend_alert.json").read_text(encoding="utf-8"))
    codes = [a["code"] for a in alert["summary"]["alerts"]]
    assert "security_slo_burn_rate_alert" in codes


def test_security_trend_gate_detects_missing_required_output(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "security_observability_policy.json").write_text(
        json.dumps({"silent_failure_detection": {"required_security_reports": ["security_slo_report.json"]}}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(security_trend_gate, "ROOT", repo)
    monkeypatch.setattr(security_trend_gate, "evidence_root", lambda: repo / "evidence")
    assert security_trend_gate.main([]) == 1
    report = json.loads((sec / "security_trend_gate.json").read_text(encoding="utf-8"))
    assert any(x.startswith("security_silent_failure_missing_output:security_slo_report.json") for x in report["findings"])
