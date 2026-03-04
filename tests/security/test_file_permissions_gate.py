from __future__ import annotations

import os
from pathlib import Path

from tooling.security import file_permissions_gate


def test_file_permissions_gate_detects_world_writable(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    p = sec / "x.txt"
    p.write_text("x\n", encoding="utf-8")
    p.chmod(0o666)
    monkeypatch.setattr(file_permissions_gate, "ROOT", repo)
    monkeypatch.setattr(file_permissions_gate, "evidence_root", lambda: repo / "evidence")
    assert file_permissions_gate.main([]) == 1


def test_file_permissions_gate_detects_symlink_and_hardlink(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    src = sec / "source.txt"
    src.write_text("x\n", encoding="utf-8")
    linked = sec / "linked.txt"
    os.link(src, linked)
    symlink = sec / "symlink.txt"
    symlink.symlink_to(src)

    monkeypatch.setattr(file_permissions_gate, "ROOT", repo)
    monkeypatch.setattr(file_permissions_gate, "evidence_root", lambda: repo / "evidence")
    assert file_permissions_gate.main([]) == 1


def test_file_permissions_gate_detects_sensitive_non_owner_only(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    p = sec / "runtime_api_state.json"
    p.write_text("{}\n", encoding="utf-8")
    p.chmod(0o644)

    monkeypatch.setattr(file_permissions_gate, "ROOT", repo)
    monkeypatch.setattr(file_permissions_gate, "evidence_root", lambda: repo / "evidence")
    assert file_permissions_gate.main([]) == 1
