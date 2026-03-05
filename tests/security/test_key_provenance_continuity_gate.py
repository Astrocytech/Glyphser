from __future__ import annotations

import json
from pathlib import Path

from tooling.security import key_provenance_continuity_gate


def _write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_key_provenance_continuity_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    gov = repo / "governance" / "security"
    _write(
        sec / "policy_signature.json",
        {"status": "PASS", "metadata": {"key_provenance": {"key_id": "k1", "adapter": "hmac", "fallback_used": False}}},
    )
    _write(
        sec / "provenance_signature.json",
        {"status": "PASS", "metadata": {"key_provenance": {"key_id": "k1", "adapter": "hmac", "fallback_used": False}}},
    )
    _write(
        sec / "evidence_attestation_index.json",
        {"status": "PASS", "key_provenance": {"key_id": "k1", "adapter": "hmac", "fallback_used": False}},
    )
    _write(
        gov / "key_rotation_epochs.json",
        {"epochs": [{"epoch_id": "epoch-1", "key_id": "k0"}, {"epoch_id": "epoch-2", "key_id": "k1", "previous_epoch_id": "epoch-1", "previous_key_id": "k0"}]},
    )
    monkeypatch.setattr(key_provenance_continuity_gate, "ROOT", repo)
    monkeypatch.setattr(key_provenance_continuity_gate, "EPOCHS", gov / "key_rotation_epochs.json")
    monkeypatch.setattr(key_provenance_continuity_gate, "evidence_root", lambda: repo / "evidence")
    assert key_provenance_continuity_gate.main([]) == 0


def test_key_provenance_continuity_gate_fails_on_mismatch(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    gov = repo / "governance" / "security"
    _write(
        sec / "policy_signature.json",
        {"status": "PASS", "metadata": {"key_provenance": {"key_id": "k1", "adapter": "hmac", "fallback_used": False}}},
    )
    _write(
        sec / "provenance_signature.json",
        {"status": "PASS", "metadata": {"key_provenance": {"key_id": "k2", "adapter": "hmac", "fallback_used": False}}},
    )
    _write(
        sec / "evidence_attestation_index.json",
        {"status": "PASS", "key_provenance": {"key_id": "k2", "adapter": "kms", "fallback_used": True}},
    )
    _write(
        gov / "key_rotation_epochs.json",
        {"epochs": [{"epoch_id": "epoch-1", "key_id": "k1"}]},
    )
    monkeypatch.setattr(key_provenance_continuity_gate, "ROOT", repo)
    monkeypatch.setattr(key_provenance_continuity_gate, "EPOCHS", gov / "key_rotation_epochs.json")
    monkeypatch.setattr(key_provenance_continuity_gate, "evidence_root", lambda: repo / "evidence")
    assert key_provenance_continuity_gate.main([]) == 1
    report = json.loads((sec / "key_provenance_continuity_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(str(item).startswith("key_id_mismatch:") for item in report["findings"])
    assert any(str(item).startswith("adapter_mismatch:") for item in report["findings"])
    assert any(str(item).startswith("fallback_signing_used:") for item in report["findings"])
