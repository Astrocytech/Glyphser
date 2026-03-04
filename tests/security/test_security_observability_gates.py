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
    monkeypatch.setattr(security_schema_normalization_gate, "ROOT", repo)
    monkeypatch.setattr(security_schema_normalization_gate, "evidence_root", lambda: repo / "evidence")
    assert security_schema_normalization_gate.main([]) == 0


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
