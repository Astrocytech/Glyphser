from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import evidence_notarization_checkpoint


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_evidence_notarization_checkpoint_passes_with_signed_matching_receipt(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)

    _write(
        sec / "long_term_retention_manifest.json",
        {"summary": {"immutable_manifest_digest": "sha256:abc123"}},
    )
    receipt = sec / "evidence_notarization_receipt.json"
    _write(
        receipt,
        {
            "notary": "glyphser-local-notary",
            "long_term_retention_manifest_digest": "sha256:abc123",
        },
    )
    signature = sign_file(receipt, key=current_key(strict=False))
    (sec / "evidence_notarization_receipt.json.sig").write_text(signature + "\n", encoding="utf-8")

    monkeypatch.setattr(evidence_notarization_checkpoint, "ROOT", repo)
    monkeypatch.setattr(evidence_notarization_checkpoint, "MANIFEST", sec / "long_term_retention_manifest.json")
    monkeypatch.setattr(evidence_notarization_checkpoint, "RECEIPT", sec / "evidence_notarization_receipt.json")
    monkeypatch.setattr(evidence_notarization_checkpoint, "evidence_root", lambda: repo / "evidence")

    assert evidence_notarization_checkpoint.main([]) == 0


def test_evidence_notarization_checkpoint_fails_on_digest_mismatch(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)

    _write(
        sec / "long_term_retention_manifest.json",
        {"summary": {"immutable_manifest_digest": "sha256:abc123"}},
    )
    receipt = sec / "evidence_notarization_receipt.json"
    _write(
        receipt,
        {
            "notary": "glyphser-local-notary",
            "long_term_retention_manifest_digest": "sha256:deadbeef",
        },
    )
    signature = sign_file(receipt, key=current_key(strict=False))
    (sec / "evidence_notarization_receipt.json.sig").write_text(signature + "\n", encoding="utf-8")

    monkeypatch.setattr(evidence_notarization_checkpoint, "ROOT", repo)
    monkeypatch.setattr(evidence_notarization_checkpoint, "MANIFEST", sec / "long_term_retention_manifest.json")
    monkeypatch.setattr(evidence_notarization_checkpoint, "RECEIPT", sec / "evidence_notarization_receipt.json")
    monkeypatch.setattr(evidence_notarization_checkpoint, "evidence_root", lambda: repo / "evidence")

    assert evidence_notarization_checkpoint.main([]) == 1
    report = json.loads((sec / "evidence_notarization_checkpoint.json").read_text(encoding="utf-8"))
    assert "notarization_receipt_digest_mismatch" in report["findings"]
