from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_super_gate


class _Proc:
    def __init__(self, rc: int) -> None:
        self.returncode = rc
        self.stdout = ""
        self.stderr = ""


def test_security_super_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    monkeypatch.setattr(security_super_gate, "ROOT", repo)
    monkeypatch.setattr(security_super_gate, "evidence_root", lambda: ev)
    monkeypatch.setattr(security_super_gate, "run_checked", lambda *a, **k: _Proc(0))
    assert security_super_gate.main([]) == 0
    out = json.loads((ev / "security" / "security_super_gate.json").read_text(encoding="utf-8"))
    assert out["status"] == "PASS"
    assert out["metadata"]["subprocess_timeout_sec"] == security_super_gate.SUPER_GATE_SUBPROCESS_TIMEOUT_SEC
    assert out["metadata"]["subprocess_max_output_bytes"] == security_super_gate.SUPER_GATE_SUBPROCESS_MAX_OUTPUT_BYTES


def test_security_super_gate_fails_on_subgate_failure(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    monkeypatch.setattr(security_super_gate, "ROOT", repo)
    monkeypatch.setattr(security_super_gate, "evidence_root", lambda: ev)

    calls = {"n": 0}

    def _run(*a, **k):
        calls["n"] += 1
        return _Proc(1 if calls["n"] == 2 else 0)

    monkeypatch.setattr(security_super_gate, "run_checked", _run)
    assert security_super_gate.main([]) == 1
