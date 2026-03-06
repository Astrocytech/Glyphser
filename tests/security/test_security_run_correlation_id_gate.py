from __future__ import annotations

import json
import os
from pathlib import Path

from tooling.security import security_run_correlation_id_gate


def _write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_security_run_correlation_id_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    fingerprint = repo / "evidence" / "security" / "security_step_execution_fingerprint.json"
    _write(
        fingerprint,
        {
            "fingerprints": [
                {
                    "job": "security-maintenance",
                    "step_index": 1,
                    "step_name": "Security gate",
                    "command_hash_sha256": "a" * 64,
                    "run_correlation_id": "1001",
                }
            ]
        },
    )

    monkeypatch.setattr(security_run_correlation_id_gate, "evidence_root", lambda: repo / "evidence")
    assert security_run_correlation_id_gate.main([]) == 0


def test_security_run_correlation_id_gate_fails_on_missing_ids(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    fingerprint = repo / "evidence" / "security" / "security_step_execution_fingerprint.json"
    _write(
        fingerprint,
        {
            "fingerprints": [
                {
                    "job": "security-maintenance",
                    "step_index": 1,
                    "step_name": "Security gate",
                    "command_hash_sha256": "a" * 64,
                    "run_correlation_id": "",
                }
            ]
        },
    )

    monkeypatch.setattr(security_run_correlation_id_gate, "evidence_root", lambda: repo / "evidence")
    assert security_run_correlation_id_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "security_run_correlation_id_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("missing_run_correlation_id:") for item in report["findings"])


def test_security_run_correlation_id_gate_fails_when_run_ids_diverge_across_reports(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _write(
        sec / "security_step_execution_fingerprint.json",
        {
            "fingerprints": [
                {
                    "job": "security-maintenance",
                    "step_index": 1,
                    "step_name": "Security gate",
                    "command_hash_sha256": "a" * 64,
                    "run_correlation_id": "1001",
                }
            ]
        },
    )
    _write(
        sec / "policy_signature.json",
        {"status": "PASS", "summary": {"run_id": "1001"}, "metadata": {"producer_version": "1.0.0"}},
    )
    _write(
        sec / "provenance_signature.json",
        {"status": "PASS", "metadata": {"run_correlation_id": "2002", "producer_version": "1.0.0"}},
    )

    monkeypatch.setattr(security_run_correlation_id_gate, "evidence_root", lambda: repo / "evidence")
    assert security_run_correlation_id_gate.main([]) == 1
    report = json.loads((sec / "security_run_correlation_id_gate.json").read_text(encoding="utf-8"))
    assert "inconsistent_run_id_across_reports:1001,2002" in report["findings"]


def test_security_run_correlation_id_gate_passes_when_shared_run_id_consistent(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _write(
        sec / "security_step_execution_fingerprint.json",
        {
            "fingerprints": [
                {
                    "job": "security-maintenance",
                    "step_index": 1,
                    "step_name": "Security gate",
                    "command_hash_sha256": "a" * 64,
                    "run_correlation_id": "3003",
                }
            ]
        },
    )
    _write(
        sec / "policy_signature.json",
        {"status": "PASS", "summary": {"run_id": "3003"}, "metadata": {"producer_version": "1.0.0"}},
    )
    _write(
        sec / "provenance_signature.json",
        {"status": "PASS", "metadata": {"run_correlation_id": "3003", "producer_version": "1.0.0"}},
    )

    monkeypatch.setattr(security_run_correlation_id_gate, "evidence_root", lambda: repo / "evidence")
    assert security_run_correlation_id_gate.main([]) == 0


def test_security_run_correlation_id_gate_fails_on_non_monotonic_generated_timestamps(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _write(
        sec / "security_step_execution_fingerprint.json",
        {
            "fingerprints": [
                {
                    "job": "security-maintenance",
                    "step_index": 1,
                    "step_name": "Security gate",
                    "command_hash_sha256": "a" * 64,
                    "run_correlation_id": "4004",
                }
            ]
        },
    )
    first = sec / "a.json"
    second = sec / "b.json"
    _write(
        first,
        {
            "status": "PASS",
            "metadata": {"generated_at_utc": "2026-03-06T02:00:00+00:00", "run_id": "4004", "producer_version": "1.0.0"},
        },
    )
    _write(
        second,
        {
            "status": "PASS",
            "metadata": {"generated_at_utc": "2026-03-06T01:00:00+00:00", "run_id": "4004", "producer_version": "1.0.0"},
        },
    )
    os.utime(first, (1000, 1000))
    os.utime(second, (2000, 2000))

    monkeypatch.setattr(security_run_correlation_id_gate, "evidence_root", lambda: repo / "evidence")
    assert security_run_correlation_id_gate.main([]) == 1
    report = json.loads((sec / "security_run_correlation_id_gate.json").read_text(encoding="utf-8"))
    assert "non_monotonic_report_timestamps:a.json->b.json" in report["findings"]


def test_security_run_correlation_id_gate_passes_on_monotonic_generated_timestamps(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _write(
        sec / "security_step_execution_fingerprint.json",
        {
            "fingerprints": [
                {
                    "job": "security-maintenance",
                    "step_index": 1,
                    "step_name": "Security gate",
                    "command_hash_sha256": "a" * 64,
                    "run_correlation_id": "5005",
                }
            ]
        },
    )
    first = sec / "a.json"
    second = sec / "b.json"
    _write(
        first,
        {
            "status": "PASS",
            "metadata": {"generated_at_utc": "2026-03-06T01:00:00+00:00", "run_id": "5005", "producer_version": "1.0.0"},
        },
    )
    _write(
        second,
        {
            "status": "PASS",
            "metadata": {"generated_at_utc": "2026-03-06T02:00:00+00:00", "run_id": "5005", "producer_version": "1.0.0"},
        },
    )
    os.utime(first, (1000, 1000))
    os.utime(second, (2000, 2000))

    monkeypatch.setattr(security_run_correlation_id_gate, "evidence_root", lambda: repo / "evidence")
    assert security_run_correlation_id_gate.main([]) == 0


def test_security_run_correlation_id_gate_fails_when_report_producer_version_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _write(
        sec / "security_step_execution_fingerprint.json",
        {
            "fingerprints": [
                {
                    "job": "security-maintenance",
                    "step_index": 1,
                    "step_name": "Security gate",
                    "command_hash_sha256": "a" * 64,
                    "run_correlation_id": "6006",
                }
            ]
        },
    )
    _write(sec / "policy_signature.json", {"status": "PASS", "summary": {"run_id": "6006"}, "metadata": {}})

    monkeypatch.setattr(security_run_correlation_id_gate, "evidence_root", lambda: repo / "evidence")
    assert security_run_correlation_id_gate.main([]) == 1
    report = json.loads((sec / "security_run_correlation_id_gate.json").read_text(encoding="utf-8"))
    assert "missing_report_producer_version:policy_signature.json" in report["findings"]


def test_security_run_correlation_id_gate_fails_when_report_producer_version_incompatible(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _write(
        sec / "security_step_execution_fingerprint.json",
        {
            "fingerprints": [
                {
                    "job": "security-maintenance",
                    "step_index": 1,
                    "step_name": "Security gate",
                    "command_hash_sha256": "a" * 64,
                    "run_correlation_id": "7007",
                }
            ]
        },
    )
    _write(
        sec / "policy_signature.json",
        {"status": "PASS", "summary": {"run_id": "7007"}, "metadata": {"producer_version": "2.1.0"}},
    )

    monkeypatch.setattr(security_run_correlation_id_gate, "evidence_root", lambda: repo / "evidence")
    assert security_run_correlation_id_gate.main([]) == 1
    report = json.loads((sec / "security_run_correlation_id_gate.json").read_text(encoding="utf-8"))
    assert "incompatible_report_producer_version:policy_signature.json:2.1.0" in report["findings"]
