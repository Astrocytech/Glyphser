from __future__ import annotations

import json
from pathlib import Path

from tooling.security import cosign_attestation_gate


def test_cosign_attestation_gate_skips_when_not_applicable(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "distribution" / "container").mkdir(parents=True)
    (repo / "evidence" / "security").mkdir(parents=True)
    monkeypatch.setattr(cosign_attestation_gate, "ROOT", repo)
    monkeypatch.setattr(cosign_attestation_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.delenv("GLYPHSER_CONTAINER_PUBLISHING_ENABLED", raising=False)

    assert cosign_attestation_gate.main([]) == 0
    out = json.loads((repo / "evidence" / "security" / "cosign_attestation_gate.json").read_text(encoding="utf-8"))
    assert out["status"] == "PASS"
    assert out["skipped"] is True


def test_cosign_attestation_gate_fails_when_publishing_enabled_without_attestations(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    (repo / "distribution" / "container").mkdir(parents=True)
    (repo / "evidence" / "security").mkdir(parents=True)
    monkeypatch.setattr(cosign_attestation_gate, "ROOT", repo)
    monkeypatch.setattr(cosign_attestation_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_CONTAINER_PUBLISHING_ENABLED", "true")

    assert cosign_attestation_gate.main([]) == 1
    out = json.loads((repo / "evidence" / "security" / "cosign_attestation_gate.json").read_text(encoding="utf-8"))
    assert out["status"] == "FAIL"
    assert out["skipped"] is False
