from __future__ import annotations

import json
from pathlib import Path

from tooling.security import attestation_digest_match_gate


def test_attestation_digest_match_gate_skips_without_manifest(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(attestation_digest_match_gate, "ROOT", repo)
    monkeypatch.setattr(
        attestation_digest_match_gate, "DIGEST_MANIFEST", repo / "distribution" / "container" / "image-digests.txt"
    )
    monkeypatch.setattr(attestation_digest_match_gate, "evidence_root", lambda: repo / "evidence")
    assert attestation_digest_match_gate.main([]) == 0


def test_attestation_digest_match_gate_fails_on_digest_mismatch(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    manifest = repo / "distribution" / "container" / "image-digests.txt"
    manifest.parent.mkdir(parents=True)
    digest = "sha256:" + "a" * 64
    manifest.write_text(f"image@{digest}\n", encoding="utf-8")
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    (sec / "build_provenance.json").write_text(json.dumps({"artifact_digests": []}) + "\n", encoding="utf-8")
    monkeypatch.setattr(attestation_digest_match_gate, "ROOT", repo)
    monkeypatch.setattr(attestation_digest_match_gate, "DIGEST_MANIFEST", manifest)
    monkeypatch.setattr(attestation_digest_match_gate, "evidence_root", lambda: repo / "evidence")
    assert attestation_digest_match_gate.main([]) == 1


def test_attestation_digest_match_gate_passes_on_exact_match(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    manifest = repo / "distribution" / "container" / "image-digests.txt"
    manifest.parent.mkdir(parents=True)
    digest = "sha256:" + "b" * 64
    manifest.write_text(f"image@{digest}\n", encoding="utf-8")
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    (sec / "build_provenance.json").write_text(json.dumps({"artifact_digests": [digest]}) + "\n", encoding="utf-8")
    monkeypatch.setattr(attestation_digest_match_gate, "ROOT", repo)
    monkeypatch.setattr(attestation_digest_match_gate, "DIGEST_MANIFEST", manifest)
    monkeypatch.setattr(attestation_digest_match_gate, "evidence_root", lambda: repo / "evidence")
    assert attestation_digest_match_gate.main([]) == 0
