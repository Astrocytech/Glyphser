from __future__ import annotations

import json
import os
import time
from pathlib import Path

from tooling.security import stale_security_test_coverage_gate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_stale_security_test_coverage_gate_passes_with_fresh_tests(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    ev = repo / "evidence"
    script = repo / "tooling" / "security" / "x_gate.py"
    test = repo / "tests" / "security" / "test_x_gate.py"
    _write_text(script, "def main(argv=None):\n    return 0\n")
    _write_text(test, "def test_x_gate():\n    assert True\n")
    _write_json(
        repo / "governance" / "security" / "stale_security_test_coverage_policy.json",
        {"max_test_age_days": 365, "tracked_scripts": [{"script": "tooling/security/x_gate.py", "test": "tests/security/test_x_gate.py"}]},
    )
    monkeypatch.setattr(stale_security_test_coverage_gate, "ROOT", repo)
    monkeypatch.setattr(
        stale_security_test_coverage_gate,
        "POLICY",
        repo / "governance" / "security" / "stale_security_test_coverage_policy.json",
    )
    monkeypatch.setattr(stale_security_test_coverage_gate, "evidence_root", lambda: ev)
    assert stale_security_test_coverage_gate.main([]) == 0


def test_stale_security_test_coverage_gate_fails_when_test_is_stale(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    ev = repo / "evidence"
    script = repo / "tooling" / "security" / "x_gate.py"
    test = repo / "tests" / "security" / "test_x_gate.py"
    _write_text(script, "def main(argv=None):\n    return 0\n")
    _write_text(test, "def test_x_gate():\n    assert True\n")
    old = time.time() - (400 * 86400)
    os.utime(test, (old, old))
    _write_json(
        repo / "governance" / "security" / "stale_security_test_coverage_policy.json",
        {"max_test_age_days": 180, "tracked_scripts": [{"script": "tooling/security/x_gate.py", "test": "tests/security/test_x_gate.py"}]},
    )
    monkeypatch.setattr(stale_security_test_coverage_gate, "ROOT", repo)
    monkeypatch.setattr(
        stale_security_test_coverage_gate,
        "POLICY",
        repo / "governance" / "security" / "stale_security_test_coverage_policy.json",
    )
    monkeypatch.setattr(stale_security_test_coverage_gate, "evidence_root", lambda: ev)
    assert stale_security_test_coverage_gate.main([]) == 1
    report = json.loads((ev / "security" / "stale_security_test_coverage_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("stale_test_coverage:") for item in report["findings"])
