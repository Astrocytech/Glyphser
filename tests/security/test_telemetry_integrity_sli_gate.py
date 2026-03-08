from __future__ import annotations

import json
from pathlib import Path

from tooling.security import telemetry_integrity_sli_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    _write(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def test_telemetry_integrity_sli_gate_passes_ratio_threshold(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _write_json(
        repo / "governance" / "security" / "security_observability_policy.json",
        {
            "telemetry_integrity": {
                "signed_reports_ratio_threshold": 0.5,
                "history_window_runs": 5,
                "ratio_drop_alert_threshold": 0.2,
            }
        },
    )
    for name in ["a.json", "b.json"]:
        _write_json(sec / name, {"status": "PASS", "findings": [], "summary": {}, "metadata": {}})
        _write(sec / f"{name}.sig", "sig\n")

    monkeypatch.setattr(telemetry_integrity_sli_gate, "ROOT", repo)
    monkeypatch.setattr(
        telemetry_integrity_sli_gate,
        "POLICY",
        repo / "governance/security/security_observability_policy.json",
    )
    monkeypatch.setattr(telemetry_integrity_sli_gate, "evidence_root", lambda: repo / "evidence")
    assert telemetry_integrity_sli_gate.main([]) == 0

    report = json.loads((sec / "telemetry_integrity_sli_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["summary"]["signed_reports_ratio"] == 1.0


def test_telemetry_integrity_sli_gate_emits_drop_alert(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _write_json(
        repo / "governance" / "security" / "security_observability_policy.json",
        {
            "telemetry_integrity": {
                "signed_reports_ratio_threshold": 0.0,
                "history_window_runs": 5,
                "ratio_drop_alert_threshold": 0.2,
            }
        },
    )
    _write_json(sec / "telemetry_integrity_sli_history.json", {"values": [1.0], "window": 5})
    _write_json(sec / "a.json", {"status": "PASS", "findings": [], "summary": {}, "metadata": {}})
    _write_json(sec / "b.json", {"status": "PASS", "findings": [], "summary": {}, "metadata": {}})
    _write(sec / "a.json.sig", "sig\n")

    monkeypatch.setattr(telemetry_integrity_sli_gate, "ROOT", repo)
    monkeypatch.setattr(
        telemetry_integrity_sli_gate,
        "POLICY",
        repo / "governance/security/security_observability_policy.json",
    )
    monkeypatch.setattr(telemetry_integrity_sli_gate, "evidence_root", lambda: repo / "evidence")
    assert telemetry_integrity_sli_gate.main([]) == 0

    alert = json.loads((sec / "telemetry_integrity_trend_alert.json").read_text(encoding="utf-8"))
    assert alert["status"] == "ALERT"
    codes = [item["code"] for item in alert["summary"]["alerts"]]
    assert "telemetry_integrity_ratio_drop" in codes
