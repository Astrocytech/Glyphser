from __future__ import annotations

import json
from pathlib import Path

from tooling.security import chaos_security_scenario_report


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_chaos_security_scenario_report_passes_when_all_scenarios_validated(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    # network_outage_tool_install_fail_safe: missing install report + failing toolchain gate
    _write(sec / "security_toolchain_gate.json", {"status": "FAIL"})
    # partial_artifact_upload_detection
    _write(sec / "upload_manifest_completeness_gate.json", {"status": "FAIL"})
    # corrupted signatures/attestations detection
    _write(sec / "evidence_attestation_gate.json", {"status": "FAIL"})

    monkeypatch.setattr(chaos_security_scenario_report, "ROOT", repo)
    monkeypatch.setattr(chaos_security_scenario_report, "evidence_root", lambda: repo / "evidence")

    assert chaos_security_scenario_report.main([]) == 0
    report = json.loads((sec / "chaos_security_scenario_report.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"


def test_chaos_security_scenario_report_warns_when_evidence_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(chaos_security_scenario_report, "ROOT", repo)
    monkeypatch.setattr(chaos_security_scenario_report, "evidence_root", lambda: repo / "evidence")

    assert chaos_security_scenario_report.main([]) == 0
    report = json.loads((sec / "chaos_security_scenario_report.json").read_text(encoding="utf-8"))
    assert report["status"] == "WARN"
    assert any(str(item).startswith("chaos_scenario_missing_evidence:") for item in report["findings"])


def test_chaos_security_scenario_report_fails_when_evidence_present_but_not_validated(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    _write(sec / "security_toolchain_install_report.json", {"status": "PASS"})
    _write(sec / "security_toolchain_gate.json", {"status": "PASS"})

    monkeypatch.setattr(chaos_security_scenario_report, "ROOT", repo)
    monkeypatch.setattr(chaos_security_scenario_report, "evidence_root", lambda: repo / "evidence")

    assert chaos_security_scenario_report.main([]) == 1
    report = json.loads((sec / "chaos_security_scenario_report.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(str(item).startswith("chaos_scenario_failed:network_outage_tool_install_fail_safe") for item in report["findings"])
