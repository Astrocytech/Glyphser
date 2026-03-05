from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, verify_file
from tooling.security import post_release_verification_checklist_artifact


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_post_release_verification_checklist_artifact_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    _write_json(sec / "security_super_gate.json", {"status": "PASS"})
    _write_json(sec / "release_handshake_artifact_gate.json", {"status": "PASS"})

    monkeypatch.setattr(post_release_verification_checklist_artifact, "ROOT", repo)
    monkeypatch.setattr(post_release_verification_checklist_artifact, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv(
        "GLYPHSER_MANDATORY_SECURITY_UPLOADS",
        '["security_super_gate.json","release_handshake_artifact_gate.json"]',
    )
    assert post_release_verification_checklist_artifact.main([]) == 0
    artifact = sec / "post_release_verification_checklist_artifact.json"
    sig = (sec / "post_release_verification_checklist_artifact.json.sig").read_text(encoding="utf-8").strip()
    assert verify_file(artifact, sig, key=current_key(strict=False))


def test_post_release_verification_checklist_artifact_fails_on_missing_required(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    _write_json(sec / "security_super_gate.json", {"status": "PASS"})

    monkeypatch.setattr(post_release_verification_checklist_artifact, "ROOT", repo)
    monkeypatch.setattr(post_release_verification_checklist_artifact, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv(
        "GLYPHSER_MANDATORY_SECURITY_UPLOADS",
        '["security_super_gate.json","release_handshake_artifact_gate.json"]',
    )
    assert post_release_verification_checklist_artifact.main([]) == 1
    report = json.loads((sec / "post_release_verification_checklist_artifact_gate.json").read_text(encoding="utf-8"))
    assert "missing_mandatory_upload:release_handshake_artifact_gate.json" in report["findings"]
