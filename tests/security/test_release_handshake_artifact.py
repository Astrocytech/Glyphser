from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, verify_file
from tooling.security import release_handshake_artifact


def test_release_handshake_artifact_passes_with_explicit_acks(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(release_handshake_artifact, "ROOT", repo)
    monkeypatch.setattr(release_handshake_artifact, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_SECURITY_OWNER", "security-owner@glyphser.local")
    monkeypatch.setenv("GLYPHSER_RELEASE_OWNER", "release-owner@glyphser.local")
    monkeypatch.setenv("GLYPHSER_RELEASE_HANDSHAKE_SECURITY_ACK", "acknowledged")
    monkeypatch.setenv("GLYPHSER_RELEASE_HANDSHAKE_RELEASE_ACK", "acknowledged")

    assert release_handshake_artifact.main([]) == 0
    artifact = repo / "evidence" / "security" / "release_handshake_artifact.json"
    sig = (repo / "evidence" / "security" / "release_handshake_artifact.json.sig").read_text(encoding="utf-8").strip()
    assert verify_file(artifact, sig, key=current_key(strict=False))


def test_release_handshake_artifact_fails_when_release_ack_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(release_handshake_artifact, "ROOT", repo)
    monkeypatch.setattr(release_handshake_artifact, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_SECURITY_OWNER", "security-owner@glyphser.local")
    monkeypatch.setenv("GLYPHSER_RELEASE_OWNER", "release-owner@glyphser.local")
    monkeypatch.setenv("GLYPHSER_RELEASE_HANDSHAKE_SECURITY_ACK", "acknowledged")
    monkeypatch.setenv("GLYPHSER_RELEASE_HANDSHAKE_RELEASE_ACK", "")

    assert release_handshake_artifact.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "release_handshake_artifact_gate.json").read_text(encoding="utf-8"))
    assert "missing_release_owner_acknowledgment" in report["findings"]
