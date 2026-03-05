from __future__ import annotations

import json
from pathlib import Path

from tooling.security import deterministic_replay_harness


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_deterministic_replay_harness_passes_when_recomputed_status_matches(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    run_dir = repo / "evidence" / "runs" / "101" / "security-maintenance"
    sec = run_dir / "security"
    _write_json(
        sec / "security_super_gate.json",
        {
            "results": [
                {
                    "cmd": ["python", "tooling/security/policy_signature_gate.py"],
                    "status": "PASS",
                    "stdout": "POLICY_SIGNATURE_GATE: PASS\nReport: /tmp/security/policy_signature.json",
                }
            ]
        },
    )
    _write_json(sec / "policy_signature.json", {"status": "PASS"})

    monkeypatch.setattr(deterministic_replay_harness, "ROOT", repo)
    monkeypatch.setattr(deterministic_replay_harness, "evidence_root", lambda: repo / "evidence")
    assert deterministic_replay_harness.main(["--run-dir", str(run_dir)]) == 0
    report = json.loads((repo / "evidence" / "security" / "deterministic_replay_harness.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["summary"]["checked_reports"] == 1
    assert report["summary"]["mismatch_count"] == 0


def test_deterministic_replay_harness_fails_on_mismatch(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    run_dir = repo / "evidence" / "runs" / "102" / "security-maintenance"
    sec = run_dir / "security"
    _write_json(
        sec / "security_super_gate.json",
        {
            "results": [
                {
                    "cmd": ["python", "tooling/security/abuse_telemetry_gate.py"],
                    "status": "PASS",
                    "stdout": "ABUSE_TELEMETRY_GATE: PASS\nReport: /tmp/security/abuse_telemetry_gate.json",
                }
            ]
        },
    )
    _write_json(sec / "abuse_telemetry_gate.json", {"status": "FAIL"})

    monkeypatch.setattr(deterministic_replay_harness, "ROOT", repo)
    monkeypatch.setattr(deterministic_replay_harness, "evidence_root", lambda: repo / "evidence")
    assert deterministic_replay_harness.main(["--run-dir", str(run_dir)]) == 1
    report = json.loads((repo / "evidence" / "security" / "deterministic_replay_harness.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(str(finding).startswith("replay_status_mismatch:") for finding in report["findings"])
