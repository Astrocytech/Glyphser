from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, verify_file
from tooling.security import manifest_pointer_meta_chain


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_manifest_pointer_meta_chain_builds_and_signs_chain(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    _write(sec / "long_term_retention_manifest.json", {"summary": {"immutable_manifest_digest": "sha256:abc"}})

    monkeypatch.setattr(manifest_pointer_meta_chain, "ROOT", repo)
    monkeypatch.setattr(manifest_pointer_meta_chain, "MANIFEST", sec / "long_term_retention_manifest.json")
    monkeypatch.setattr(manifest_pointer_meta_chain, "CHAIN", sec / "manifest_pointer_meta_chain.json")
    monkeypatch.setattr(manifest_pointer_meta_chain, "evidence_root", lambda: repo / "evidence")

    assert manifest_pointer_meta_chain.main([]) == 0
    report = json.loads((sec / "manifest_pointer_meta_chain.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["summary"]["chain_length"] == 1
    sig = (sec / "manifest_pointer_meta_chain.json.sig").read_text(encoding="utf-8").strip()
    assert verify_file(sec / "manifest_pointer_meta_chain.json", sig, key=current_key(strict=False))


def test_manifest_pointer_meta_chain_fails_without_manifest(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(manifest_pointer_meta_chain, "ROOT", repo)
    monkeypatch.setattr(manifest_pointer_meta_chain, "MANIFEST", sec / "long_term_retention_manifest.json")
    monkeypatch.setattr(manifest_pointer_meta_chain, "CHAIN", sec / "manifest_pointer_meta_chain.json")
    monkeypatch.setattr(manifest_pointer_meta_chain, "evidence_root", lambda: repo / "evidence")

    assert manifest_pointer_meta_chain.main([]) == 1
    report = json.loads((sec / "manifest_pointer_meta_chain.json").read_text(encoding="utf-8"))
    assert "missing_long_term_retention_manifest" in report["findings"]
