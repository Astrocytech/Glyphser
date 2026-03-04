from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key
from tooling.security import evidence_attestation_gate, evidence_attestation_index


def test_evidence_attestation_index_and_gate_pass(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "evidence" / "security").mkdir(parents=True)
    (repo / "evidence" / "security" / "alpha.json").write_text(json.dumps({"ok": True}) + "\n", encoding="utf-8")
    (repo / "evidence" / "security" / "beta.json").write_text(json.dumps({"ok": True}) + "\n", encoding="utf-8")
    monkeypatch.setattr(evidence_attestation_index, "ROOT", repo)
    monkeypatch.setattr(evidence_attestation_index, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(evidence_attestation_index, "current_key", lambda strict=False: current_key(strict=False))
    assert evidence_attestation_index.main([]) == 0

    monkeypatch.setattr(evidence_attestation_gate, "ROOT", repo)
    monkeypatch.setattr(evidence_attestation_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(evidence_attestation_gate, "current_key", lambda strict=False: current_key(strict=False))
    assert evidence_attestation_gate.main([]) == 0


def test_evidence_attestation_gate_fails_on_tamper(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "evidence" / "security").mkdir(parents=True)
    target = repo / "evidence" / "security" / "alpha.json"
    target.write_text(json.dumps({"ok": True}) + "\n", encoding="utf-8")
    monkeypatch.setattr(evidence_attestation_index, "ROOT", repo)
    monkeypatch.setattr(evidence_attestation_index, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(evidence_attestation_index, "current_key", lambda strict=False: current_key(strict=False))
    assert evidence_attestation_index.main([]) == 0

    target.write_text(json.dumps({"ok": False}) + "\n", encoding="utf-8")

    monkeypatch.setattr(evidence_attestation_gate, "ROOT", repo)
    monkeypatch.setattr(evidence_attestation_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(evidence_attestation_gate, "current_key", lambda strict=False: current_key(strict=False))
    assert evidence_attestation_gate.main([]) == 1
