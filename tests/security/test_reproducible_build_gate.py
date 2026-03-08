from __future__ import annotations

import json
from pathlib import Path

from tooling.security import reproducible_build_gate


def test_reproducible_build_gate_passes_with_matching_hashes(monkeypatch, tmp_path: Path) -> None:
    def _fake_run_build(_tag: str):
        return 0, "abc123", "", ""

    monkeypatch.setattr(reproducible_build_gate, "_run_build", _fake_run_build)
    monkeypatch.setattr(reproducible_build_gate, "evidence_root", lambda: tmp_path / "evidence")
    assert reproducible_build_gate.main() == 0
    payload = json.loads((tmp_path / "evidence" / "security" / "reproducible_build.json").read_text(encoding="utf-8"))
    assert payload["status"] == "PASS"


def test_reproducible_build_gate_fails_on_hash_mismatch(monkeypatch, tmp_path: Path) -> None:
    state = {"count": 0}

    def _fake_run_build(_tag: str):
        state["count"] += 1
        return 0, f"sha-{state['count']}", "", ""

    monkeypatch.setattr(reproducible_build_gate, "_run_build", _fake_run_build)
    monkeypatch.setattr(reproducible_build_gate, "evidence_root", lambda: tmp_path / "evidence")
    assert reproducible_build_gate.main() == 1
