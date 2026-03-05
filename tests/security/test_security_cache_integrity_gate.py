from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_cache_integrity_gate


class _Proc:
    def __init__(self, rc: int, out: str) -> None:
        self.returncode = rc
        self.stdout = out
        self.stderr = ""


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_security_cache_integrity_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    _write_json(repo / "tooling" / "security" / "security_toolchain_lock.json", {"bandit": {"version": "1.9.4"}})
    monkeypatch.setattr(security_cache_integrity_gate, "ROOT", repo)
    monkeypatch.setattr(security_cache_integrity_gate, "LOCK", repo / "tooling" / "security" / "security_toolchain_lock.json")
    monkeypatch.setattr(
        security_cache_integrity_gate,
        "run_checked",
        lambda *a, **k: _Proc(0, json.dumps([{"name": "bandit", "version": "1.9.4"}])),
    )
    monkeypatch.setattr(security_cache_integrity_gate, "evidence_root", lambda: ev)

    assert security_cache_integrity_gate.main([]) == 0


def test_security_cache_integrity_gate_fails_on_version_mismatch(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    _write_json(repo / "tooling" / "security" / "security_toolchain_lock.json", {"bandit": {"version": "1.9.4"}})
    monkeypatch.setattr(security_cache_integrity_gate, "ROOT", repo)
    monkeypatch.setattr(security_cache_integrity_gate, "LOCK", repo / "tooling" / "security" / "security_toolchain_lock.json")
    monkeypatch.setattr(
        security_cache_integrity_gate,
        "run_checked",
        lambda *a, **k: _Proc(0, json.dumps([{"name": "bandit", "version": "1.9.3"}])),
    )
    monkeypatch.setattr(security_cache_integrity_gate, "evidence_root", lambda: ev)

    assert security_cache_integrity_gate.main([]) == 1
    report = json.loads((ev / "security" / "security_cache_integrity_gate.json").read_text(encoding="utf-8"))
    assert any(item.startswith("locked_package_version_mismatch:bandit") for item in report["findings"])
