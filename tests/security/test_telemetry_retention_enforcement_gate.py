from __future__ import annotations

import json
import os
import time
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import telemetry_retention_enforcement_gate


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sign(path: Path) -> None:
    path.with_suffix(".json.sig").write_text(sign_file(path, key=current_key(strict=False)) + "\n", encoding="utf-8")


def test_telemetry_retention_enforcement_gate_passes_for_fresh_sensitive_telemetry(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "telemetry_retention_policy.json"
    _write(
        policy,
        {
            "ephemeral_sensitive_telemetry": {
                "scan_globs": ["evidence/security/security_events.jsonl"],
                "max_age_hours": 24,
            }
        },
    )
    _sign(policy)
    ev = repo / "evidence" / "security" / "security_events.jsonl"
    ev.parent.mkdir(parents=True, exist_ok=True)
    ev.write_text("{}\n", encoding="utf-8")

    monkeypatch.setattr(telemetry_retention_enforcement_gate, "ROOT", repo)
    monkeypatch.setattr(telemetry_retention_enforcement_gate, "POLICY", policy)
    monkeypatch.setattr(telemetry_retention_enforcement_gate, "evidence_root", lambda: repo / "evidence")
    assert telemetry_retention_enforcement_gate.main([]) == 0


def test_telemetry_retention_enforcement_gate_fails_for_stale_sensitive_telemetry(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "telemetry_retention_policy.json"
    _write(
        policy,
        {
            "ephemeral_sensitive_telemetry": {
                "scan_globs": ["evidence/security/security_events.jsonl"],
                "max_age_hours": 1,
            }
        },
    )
    _sign(policy)
    ev = repo / "evidence" / "security" / "security_events.jsonl"
    ev.parent.mkdir(parents=True, exist_ok=True)
    ev.write_text("{}\n", encoding="utf-8")
    old_ts = time.time() - (3 * 3600)
    os.utime(ev, (old_ts, old_ts))

    monkeypatch.setattr(telemetry_retention_enforcement_gate, "ROOT", repo)
    monkeypatch.setattr(telemetry_retention_enforcement_gate, "POLICY", policy)
    monkeypatch.setattr(telemetry_retention_enforcement_gate, "evidence_root", lambda: repo / "evidence")
    assert telemetry_retention_enforcement_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "telemetry_retention_enforcement_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("stale_sensitive_telemetry:") for item in report["findings"])
