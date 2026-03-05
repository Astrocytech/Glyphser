from __future__ import annotations

import json
from pathlib import Path

from tooling.security import time_source_attestation_gate


def test_time_source_attestation_gate_passes_without_skew(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    monkeypatch.setattr(time_source_attestation_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        time_source_attestation_gate,
        "load_stage_s_policy",
        lambda: {"time_attestation": {"max_skew_seconds": 300, "trusted_unix_time_env": "GLYPHSER_TRUSTED_UNIX_TIME"}},
    )
    monkeypatch.setattr(time_source_attestation_gate.time, "time", lambda: 1000.0)
    monkeypatch.setenv("GLYPHSER_TRUSTED_UNIX_TIME", "1000")
    assert time_source_attestation_gate.main([]) == 0
    stale_artifact = json.loads((sec / "stale_clock_detection_artifact.json").read_text(encoding="utf-8"))
    assert stale_artifact["status"] == "PASS"
    assert stale_artifact["summary"]["stale_clock_detected"] is False


def test_time_source_attestation_gate_fails_on_clock_consistency_violation(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    monkeypatch.setattr(time_source_attestation_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        time_source_attestation_gate,
        "load_stage_s_policy",
        lambda: {"time_attestation": {"max_skew_seconds": 300, "trusted_unix_time_env": "GLYPHSER_TRUSTED_UNIX_TIME"}},
    )
    monkeypatch.setattr(time_source_attestation_gate.time, "time", lambda: 1000.0)
    monkeypatch.setenv("GLYPHSER_TRUSTED_UNIX_TIME", "1000")
    monkeypatch.setattr(
        time_source_attestation_gate,
        "clock_consistency_violation",
        lambda _now: "clock_consistency_violation:wall_vs_monotonic_drift_seconds:15.000:tolerance_seconds:5.000",
    )
    assert time_source_attestation_gate.main([]) == 1
    report = json.loads((sec / "time_source_attestation_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("clock_consistency_violation:") for item in report["findings"])


def test_time_source_attestation_gate_writes_stale_clock_remediation_artifact(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    monkeypatch.setattr(time_source_attestation_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        time_source_attestation_gate,
        "load_stage_s_policy",
        lambda: {
            "time_attestation": {
                "max_skew_seconds": 300,
                "stale_clock_threshold_seconds": 600,
                "trusted_unix_time_env": "GLYPHSER_TRUSTED_UNIX_TIME",
            }
        },
    )
    monkeypatch.setattr(time_source_attestation_gate.time, "time", lambda: 2000.0)
    monkeypatch.setenv("GLYPHSER_TRUSTED_UNIX_TIME", "1000")
    assert time_source_attestation_gate.main([]) == 1
    stale_artifact = json.loads((sec / "stale_clock_detection_artifact.json").read_text(encoding="utf-8"))
    assert stale_artifact["status"] == "FAIL"
    assert stale_artifact["summary"]["stale_clock_detected"] is True
    guidance = stale_artifact["summary"]["remediation_guidance"]
    assert isinstance(guidance, list)
    assert len(guidance) >= 3


def test_time_source_attestation_gate_applies_environment_specific_max_skew(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    monkeypatch.setattr(time_source_attestation_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        time_source_attestation_gate,
        "load_stage_s_policy",
        lambda: {
            "time_attestation": {
                "max_skew_seconds": 300,
                "environment_var": "GLYPHSER_ENV",
                "max_skew_seconds_by_environment": {"production": 60},
                "trusted_unix_time_env": "GLYPHSER_TRUSTED_UNIX_TIME",
            }
        },
    )
    monkeypatch.setenv("GLYPHSER_ENV", "production")
    monkeypatch.setattr(time_source_attestation_gate.time, "time", lambda: 1000.0)
    monkeypatch.setenv("GLYPHSER_TRUSTED_UNIX_TIME", "1100")
    assert time_source_attestation_gate.main([]) == 1
    report = json.loads((sec / "time_source_attestation_gate.json").read_text(encoding="utf-8"))
    assert "clock_skew_exceeds_threshold:100" in report["findings"]
    assert report["summary"]["max_skew_seconds"] == 60
    assert report["summary"]["environment"] == "production"
