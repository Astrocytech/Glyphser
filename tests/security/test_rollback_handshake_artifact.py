from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, verify_file
from tooling.security import rollback_handshake_artifact


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_rollback_handshake_artifact_passes_with_revalidations(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    _write_json(sec / "provenance_signature.json", {"status": "PASS"})
    _write_json(sec / "policy_signature.json", {"status": "PASS"})
    _write_json(sec / "release_rollback_provenance_gate.json", {"status": "PASS"})

    monkeypatch.setattr(rollback_handshake_artifact, "ROOT", repo)
    monkeypatch.setattr(rollback_handshake_artifact, "evidence_root", lambda: repo / "evidence")
    assert rollback_handshake_artifact.main([]) == 0
    artifact = sec / "rollback_handshake_artifact.json"
    sig = (sec / "rollback_handshake_artifact.json.sig").read_text(encoding="utf-8").strip()
    assert verify_file(artifact, sig, key=current_key(strict=False))


def test_rollback_handshake_artifact_fails_when_policy_revalidation_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    _write_json(sec / "provenance_signature.json", {"status": "PASS"})
    _write_json(sec / "release_rollback_provenance_gate.json", {"status": "PASS"})

    monkeypatch.setattr(rollback_handshake_artifact, "ROOT", repo)
    monkeypatch.setattr(rollback_handshake_artifact, "evidence_root", lambda: repo / "evidence")
    assert rollback_handshake_artifact.main([]) == 1
    report = json.loads((sec / "rollback_handshake_artifact_gate.json").read_text(encoding="utf-8"))
    assert "missing_revalidation_artifact:policy_signature.json" in report["findings"]
