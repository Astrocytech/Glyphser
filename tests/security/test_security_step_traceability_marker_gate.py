from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_step_traceability_marker_gate


def _write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_security_step_traceability_marker_gate_passes(monkeypatch, tmp_path: Path) -> None:
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
                    "start_marker": "STEP_START:security-maintenance:1:abc",
                    "end_marker": "STEP_END:security-maintenance:1:abc",
                }
            ]
        },
    )

    monkeypatch.setattr(security_step_traceability_marker_gate, "evidence_root", lambda: repo / "evidence")
    assert security_step_traceability_marker_gate.main([]) == 0


def test_security_step_traceability_marker_gate_fails_when_markers_missing(monkeypatch, tmp_path: Path) -> None:
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
                    "start_marker": "",
                    "end_marker": "bad",
                }
            ]
        },
    )

    monkeypatch.setattr(security_step_traceability_marker_gate, "evidence_root", lambda: repo / "evidence")
    assert security_step_traceability_marker_gate.main([]) == 1
    report = json.loads(
        (repo / "evidence" / "security" / "security_step_traceability_marker_gate.json").read_text(encoding="utf-8")
    )
    assert any(str(item).startswith("missing_step_start_marker:") for item in report["findings"])
    assert any(str(item).startswith("missing_step_end_marker:") for item in report["findings"])
