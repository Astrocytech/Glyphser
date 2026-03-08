from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from tooling.security import report_io
from tooling.security.report_io import write_json_report


def test_write_json_report_writes_sorted_json_with_newline(tmp_path: Path) -> None:
    out = tmp_path / "security" / "report.json"
    write_json_report(out, {"b": 1, "a": {"z": 2, "y": 3}})
    content = out.read_text(encoding="utf-8")
    assert content.endswith("\n")
    assert content.index('"a"') < content.index('"b"')
    parsed = json.loads(content)
    assert parsed["a"]["y"] == 3


def test_write_json_report_replaces_existing_file_atomically(tmp_path: Path) -> None:
    out = tmp_path / "security" / "report.json"
    write_json_report(out, {"version": 1})
    first = out.read_text(encoding="utf-8")
    write_json_report(out, {"version": 2})
    second = out.read_text(encoding="utf-8")
    assert first != second
    assert json.loads(second)["version"] == 2


def test_write_json_report_auto_normalizes_security_report_shape(tmp_path: Path) -> None:
    out = tmp_path / "security" / "gate.json"
    write_json_report(out, {"status": "PASS"})
    parsed = json.loads(out.read_text(encoding="utf-8"))
    assert parsed["schema_version"] == 1
    assert parsed["findings"] == []
    assert parsed["summary"] == {}
    assert "generated_at_utc" in parsed["metadata"]


def test_write_json_report_adds_env_normalization_metadata(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("TZ", "UTC")
    monkeypatch.setenv("LC_ALL", "C.UTF-8")
    monkeypatch.setenv("LANG", "C.UTF-8")
    out = tmp_path / "security" / "gate.json"
    write_json_report(out, {"status": "PASS", "metadata": {}})
    parsed = json.loads(out.read_text(encoding="utf-8"))
    meta = parsed["metadata"]
    assert meta["tz"] == "UTC"
    assert meta["lc_all"] == "C.UTF-8"
    assert meta["lang"] == "C.UTF-8"
    assert "generated_at_utc" in meta


def test_clock_consistency_violation_is_none_when_drift_within_tolerance(monkeypatch) -> None:
    now = datetime(2026, 3, 5, tzinfo=UTC)
    monkeypatch.setattr(report_io, "_MONOTONIC_BASE", 100.0)
    monkeypatch.setattr(report_io, "_WALL_CLOCK_BASE", now - timedelta(seconds=20))
    monkeypatch.setattr(report_io.time, "monotonic", lambda: 120.0)
    assert report_io.clock_consistency_violation(now, tolerance_seconds=0.5) is None


def test_clock_consistency_violation_flags_large_drift(monkeypatch) -> None:
    now = datetime(2026, 3, 5, tzinfo=UTC)
    monkeypatch.setattr(report_io, "_MONOTONIC_BASE", 100.0)
    monkeypatch.setattr(report_io, "_WALL_CLOCK_BASE", now - timedelta(seconds=1))
    monkeypatch.setattr(report_io.time, "monotonic", lambda: 120.0)
    issue = report_io.clock_consistency_violation(now, tolerance_seconds=0.5)
    assert isinstance(issue, str)
    assert issue.startswith("clock_consistency_violation:")


def test_write_json_report_derives_machine_readable_error_codes(tmp_path: Path) -> None:
    out = tmp_path / "security" / "gate.json"
    write_json_report(
        out,
        {
            "status": "FAIL",
            "findings": ["missing_metadata:OPERATIONS.md", "auth_failure_spike:14"],
        },
    )
    parsed = json.loads(out.read_text(encoding="utf-8"))
    meta = parsed["metadata"]
    assert meta["error_code_version"] == "v1"
    assert meta["error_codes"] == [
        "sec_missing_metadata_operations_md",
        "sec_auth_failure_spike_14",
    ]


def test_write_json_report_distinguishes_infra_vs_control_failures(tmp_path: Path) -> None:
    out = tmp_path / "security" / "gate.json"
    write_json_report(
        out,
        {
            "status": "FAIL",
            "findings": ["network_timeout:upstream_scanner", "invalid_metadata_signature:OPERATIONS.meta.json"],
        },
    )
    parsed = json.loads(out.read_text(encoding="utf-8"))
    domains = parsed["metadata"]["failure_domains"]
    assert "sec_network_timeout_upstream_scanner" in domains["transient_infra_failures"]
    assert "sec_invalid_metadata_signature_operations_meta_json" in domains["security_control_failures"]


def test_write_json_report_adds_top_level_failure_classification(tmp_path: Path) -> None:
    out = tmp_path / "security" / "gate.json"
    write_json_report(
        out,
        {
            "status": "FAIL",
            "findings": [
                "missing_tool:semgrep",
                "network_timeout:scanner",
                "policy_signature_invalid",
                "stale_attestation:evidence/security/a.sig:999h",
            ],
        },
    )
    parsed = json.loads(out.read_text(encoding="utf-8"))
    meta = parsed["metadata"]
    assert meta["failure_classification"] == "prereq_failure"
    categories = set(meta["failure_classification_set"])
    assert {"prereq_failure", "infra_failure", "policy_failure", "control_failure"}.issubset(categories)


def test_write_json_report_adds_control_family_tags(tmp_path: Path) -> None:
    out = tmp_path / "security" / "gate.json"
    write_json_report(
        out,
        {
            "status": "FAIL",
            "findings": ["auth_failure_spike:20", "signature_mismatch:artifact.sig"],
            "metadata": {"gate": "provenance_signature_gate"},
        },
    )
    parsed = json.loads(out.read_text(encoding="utf-8"))
    tags = set(parsed["metadata"]["control_family_tags"])
    assert "identity" in tags
    assert "provenance" in tags


def test_write_json_report_adds_escalation_matrix_to_fail_reports(tmp_path: Path) -> None:
    out = tmp_path / "security" / "gate.json"
    write_json_report(out, {"status": "FAIL", "findings": ["policy_signature_invalid"]})
    parsed = json.loads(out.read_text(encoding="utf-8"))
    matrix = parsed["metadata"]["escalation_matrix"]
    assert isinstance(matrix, dict)
    assert "severity_levels" in matrix
