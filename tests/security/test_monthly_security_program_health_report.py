from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, verify_file
from tooling.security import monthly_security_program_health_report


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_monthly_security_program_health_report_is_signed(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _write(sec / "security_dashboard.json", {"status": "PASS", "summary": {"kpis": {"control_coverage_ratio": 1.0}}})
    _write(sec / "security_slo_report.json", {"status": "PASS"})
    _write(sec / "security_trend_gate.json", {"status": "PASS"})
    _write(sec / "security_verification_summary.json", {"status": "PASS"})

    monkeypatch.setenv("GLYPHSER_FIXED_UTC", "2026-03-06T00:00:00+00:00")
    monkeypatch.setattr(monthly_security_program_health_report, "ROOT", repo)
    monkeypatch.setattr(monthly_security_program_health_report, "evidence_root", lambda: repo / "evidence")
    assert monthly_security_program_health_report.main([]) == 0

    report = sec / "monthly_security_program_health_report.json"
    sig = sec / "monthly_security_program_health_report.json.sig"
    assert report.exists() and sig.exists()
    assert verify_file(report, sig.read_text(encoding="utf-8").strip(), key=current_key(strict=False))
    payload = json.loads(report.read_text(encoding="utf-8"))
    assert payload["summary"]["month"] == "2026-03"
    assert payload["summary"]["kpis"]["control_coverage_ratio"] == 1.0


def test_monthly_security_program_health_report_warns_when_dashboard_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(monthly_security_program_health_report, "ROOT", repo)
    monkeypatch.setattr(monthly_security_program_health_report, "evidence_root", lambda: repo / "evidence")
    assert monthly_security_program_health_report.main([]) == 1
    payload = json.loads((sec / "monthly_security_program_health_report.json").read_text(encoding="utf-8"))
    assert payload["status"] == "WARN"
    assert "missing_security_dashboard" in payload["findings"]
