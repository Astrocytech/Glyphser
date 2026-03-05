from __future__ import annotations

import json
from pathlib import Path

from tooling.security import deterministic_replay_harness, replay_nondeterministic_field_drift_gate


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _seed_replay_inputs(run_dir: Path) -> None:
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


def test_replay_nondeterministic_field_drift_gate_passes_when_static_fields_match(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    run_dir = repo / "evidence" / "runs" / "201" / "security-maintenance"
    _seed_replay_inputs(run_dir)

    monkeypatch.setattr(deterministic_replay_harness, "ROOT", repo)
    monkeypatch.setattr(deterministic_replay_harness, "evidence_root", lambda: run_dir)
    assert deterministic_replay_harness.main(["--run-dir", str(run_dir)]) == 0

    monkeypatch.setattr(replay_nondeterministic_field_drift_gate, "ROOT", repo)
    monkeypatch.setattr(replay_nondeterministic_field_drift_gate, "evidence_root", lambda: repo / "evidence")
    assert replay_nondeterministic_field_drift_gate.main(["--run-dir", str(run_dir)]) == 0

    report = json.loads(
        (repo / "evidence" / "security" / "replay_nondeterministic_field_drift_gate.json").read_text(encoding="utf-8")
    )
    assert report["status"] == "PASS"


def test_replay_nondeterministic_field_drift_gate_fails_when_persisted_checks_drift(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    run_dir = repo / "evidence" / "runs" / "202" / "security-maintenance"
    _seed_replay_inputs(run_dir)

    monkeypatch.setattr(deterministic_replay_harness, "ROOT", repo)
    monkeypatch.setattr(deterministic_replay_harness, "evidence_root", lambda: run_dir)
    assert deterministic_replay_harness.main(["--run-dir", str(run_dir)]) == 0

    persisted = json.loads((run_dir / "security" / "deterministic_replay_harness.json").read_text(encoding="utf-8"))
    persisted["checks"][0]["recomputed_status"] = "FAIL"
    _write_json(run_dir / "security" / "deterministic_replay_harness.json", persisted)

    monkeypatch.setattr(replay_nondeterministic_field_drift_gate, "ROOT", repo)
    monkeypatch.setattr(replay_nondeterministic_field_drift_gate, "evidence_root", lambda: repo / "evidence")
    assert replay_nondeterministic_field_drift_gate.main(["--run-dir", str(run_dir)]) == 1

    report = json.loads(
        (repo / "evidence" / "security" / "replay_nondeterministic_field_drift_gate.json").read_text(encoding="utf-8")
    )
    assert report["status"] == "FAIL"
    assert "nondeterministic_field_drift:checks" in report["findings"]
