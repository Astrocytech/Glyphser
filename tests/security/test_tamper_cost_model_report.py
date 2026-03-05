from __future__ import annotations

import json
from pathlib import Path

from tooling.security import tamper_cost_model_report


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_tamper_cost_model_report_passes_with_required_dimensions(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _write(sec / "security_super_gate.json", {"status": "PASS"})
    _write(sec / "provenance_signature.json", {"status": "PASS"})
    _write(sec / "evidence_attestation_gate.json", {"status": "PASS"})
    _write(sec / "rolling_merkle_checkpoints.json", {"status": "PASS"})

    monkeypatch.setattr(tamper_cost_model_report, "evidence_root", lambda: repo / "evidence")
    assert tamper_cost_model_report.main([]) == 0

    report = json.loads((sec / "tamper_cost_model_report.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    summary = report["summary"]
    assert "time_to_detect" in summary
    assert "blast_radius" in summary
    assert "required_trust_assumptions" in summary


def test_tamper_cost_model_report_fails_when_core_signals_fail(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _write(sec / "security_super_gate.json", {"status": "FAIL"})
    _write(sec / "provenance_signature.json", {"status": "PASS"})
    _write(sec / "evidence_attestation_gate.json", {"status": "PASS"})
    _write(sec / "rolling_merkle_checkpoints.json", {"status": "PASS"})

    monkeypatch.setattr(tamper_cost_model_report, "evidence_root", lambda: repo / "evidence")
    assert tamper_cost_model_report.main([]) == 1

    report = json.loads((sec / "tamper_cost_model_report.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(item.startswith("failed_signals:") for item in report["findings"])
