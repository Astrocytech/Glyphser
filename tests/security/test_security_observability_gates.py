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
