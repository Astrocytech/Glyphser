from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tooling.security import security_toolchain_gate


def _version_hash(name: str, version: str) -> str:
    return "sha256:" + hashlib.sha256(f"{name}=={version}".encode("utf-8")).hexdigest()


def test_security_toolchain_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "tooling" / "security").mkdir(parents=True)
    lock = {
        "bandit": {"version": "1.0.0", "version_hash": _version_hash("bandit", "1.0.0")},
        "pip-audit": {"version": "2.0.0", "version_hash": _version_hash("pip-audit", "2.0.0")},
    }
    (repo / "tooling" / "security" / "security_toolchain_lock.json").write_text(
        json.dumps(lock) + "\n", encoding="utf-8"
    )
    monkeypatch.setattr(security_toolchain_gate, "ROOT", repo)
    monkeypatch.setattr(security_toolchain_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        security_toolchain_gate.metadata,
        "version",
        lambda pkg: {"bandit": "1.0.0", "pip-audit": "2.0.0"}[pkg],
    )
    assert security_toolchain_gate.main([]) == 0


def test_security_toolchain_gate_fails_on_mismatch(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "tooling" / "security").mkdir(parents=True)
    lock = {"bandit": {"version": "1.0.0", "version_hash": _version_hash("bandit", "1.0.0")}}
    (repo / "tooling" / "security" / "security_toolchain_lock.json").write_text(
        json.dumps(lock) + "\n", encoding="utf-8"
    )
    monkeypatch.setattr(security_toolchain_gate, "ROOT", repo)
    monkeypatch.setattr(security_toolchain_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(security_toolchain_gate.metadata, "version", lambda pkg: "1.0.1")
    assert security_toolchain_gate.main([]) == 1
