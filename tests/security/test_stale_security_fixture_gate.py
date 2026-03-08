from __future__ import annotations

import json
import os
import time
from pathlib import Path

from tooling.security import stale_security_fixture_gate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_stale_security_fixture_gate_passes_with_fresh_fixtures(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    ev = repo / "evidence"
    gate = repo / "tooling" / "security" / "x_gate.py"
    fixture = repo / "tests" / "security" / "corpus" / "fixture.json"
    _write_text(gate, "def main(argv=None):\n    return 0\n")
    _write_text(fixture, '{"ok": true}\n')
    gate_time = time.time() - (2 * 86400)
    fixture_time = time.time() - 3600
    os.utime(gate, (gate_time, gate_time))
    os.utime(fixture, (fixture_time, fixture_time))
    _write_json(
        repo / "tooling" / "security" / "stale_security_fixture_policy.json",
        {
            "max_fixture_lag_days": 14,
            "tracked_gate_fixtures": [
                {"gate": "tooling/security/x_gate.py", "fixtures": ["tests/security/corpus/fixture.json"]}
            ],
        },
    )
    monkeypatch.setattr(stale_security_fixture_gate, "ROOT", repo)
    monkeypatch.setattr(
        stale_security_fixture_gate,
        "POLICY",
        repo / "tooling" / "security" / "stale_security_fixture_policy.json",
    )
    monkeypatch.setattr(stale_security_fixture_gate, "evidence_root", lambda: ev)
    assert stale_security_fixture_gate.main([]) == 0


def test_stale_security_fixture_gate_fails_when_gate_is_newer_than_fixture(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    ev = repo / "evidence"
    gate = repo / "tooling" / "security" / "x_gate.py"
    fixture = repo / "tests" / "security" / "corpus" / "fixture.json"
    _write_text(gate, "def main(argv=None):\n    return 0\n")
    _write_text(fixture, '{"ok": true}\n')
    fixture_time = time.time() - (40 * 86400)
    gate_time = time.time()
    os.utime(gate, (gate_time, gate_time))
    os.utime(fixture, (fixture_time, fixture_time))
    _write_json(
        repo / "tooling" / "security" / "stale_security_fixture_policy.json",
        {
            "max_fixture_lag_days": 14,
            "tracked_gate_fixtures": [
                {"gate": "tooling/security/x_gate.py", "fixtures": ["tests/security/corpus/fixture.json"]}
            ],
        },
    )
    monkeypatch.setattr(stale_security_fixture_gate, "ROOT", repo)
    monkeypatch.setattr(
        stale_security_fixture_gate,
        "POLICY",
        repo / "tooling" / "security" / "stale_security_fixture_policy.json",
    )
    monkeypatch.setattr(stale_security_fixture_gate, "evidence_root", lambda: ev)
    assert stale_security_fixture_gate.main([]) == 1
    report = json.loads((ev / "security" / "stale_security_fixture_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("stale_fixture_after_gate_change:") for item in report["findings"])
