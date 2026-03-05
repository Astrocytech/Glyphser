from __future__ import annotations

import json
from pathlib import Path

from tooling.security import merkle_checkpoint_continuity_gate


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_merkle_checkpoint_continuity_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    prev = "a" * 64
    curr = "b" * 64
    _write(
        sec / "rolling_merkle_checkpoints.json",
        {"status": "PASS", "summary": {"previous_root": prev, "final_root": curr}},
    )

    monkeypatch.setenv("GLYPHSER_EXPECTED_PREVIOUS_MERKLE_ROOT", prev)
    monkeypatch.setattr(merkle_checkpoint_continuity_gate, "ROOT", repo)
    monkeypatch.setattr(merkle_checkpoint_continuity_gate, "evidence_root", lambda: repo / "evidence")
    assert merkle_checkpoint_continuity_gate.main([]) == 0

    gate = json.loads((sec / "merkle_checkpoint_continuity_gate.json").read_text(encoding="utf-8"))
    assert gate["status"] == "PASS"


def test_merkle_checkpoint_continuity_gate_fails_on_mismatch(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _write(
        sec / "rolling_merkle_checkpoints.json",
        {"status": "PASS", "summary": {"previous_root": "c" * 64, "final_root": "d" * 64}},
    )

    monkeypatch.setenv("GLYPHSER_EXPECTED_PREVIOUS_MERKLE_ROOT", "e" * 64)
    monkeypatch.setattr(merkle_checkpoint_continuity_gate, "ROOT", repo)
    monkeypatch.setattr(merkle_checkpoint_continuity_gate, "evidence_root", lambda: repo / "evidence")
    assert merkle_checkpoint_continuity_gate.main([]) == 1

    gate = json.loads((sec / "merkle_checkpoint_continuity_gate.json").read_text(encoding="utf-8"))
    assert gate["status"] == "FAIL"
    assert "checkpoint_continuity_mismatch" in gate["findings"]
