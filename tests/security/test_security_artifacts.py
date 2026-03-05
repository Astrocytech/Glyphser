from __future__ import annotations

import json
from pathlib import Path

import pytest

from runtime.glyphser.security.artifact_signing import verify_file
from tooling.security import security_artifacts


def _seed_repo(repo: Path) -> None:
    (repo / "requirements.lock").write_text("pytest==8.3.3\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text("[project]\nname='glyphser'\nversion='0.0.0'\n", encoding="utf-8")


def test_security_artifacts_generates_signed_and_verified_sbom(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    _seed_repo(repo)

    monkeypatch.setattr(security_artifacts, "ROOT", repo)
    monkeypatch.setattr(security_artifacts, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(security_artifacts, "current_key", lambda strict=False: b"unit-test-key")

    assert security_artifacts.main() == 0
    sec = repo / "evidence" / "security"
    sbom_path = sec / "sbom.json"
    sig_path = sec / "sbom.json.sig"
    assert sbom_path.exists()
    assert sig_path.exists()

    sig = sig_path.read_text(encoding="utf-8").strip()
    assert verify_file(sbom_path, sig, key=b"unit-test-key")
    payload = json.loads(sbom_path.read_text(encoding="utf-8"))
    assert payload["format"] == "glyphser-sbom-v1"


def test_security_artifacts_fails_when_generated_signature_does_not_verify(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    _seed_repo(repo)

    monkeypatch.setattr(security_artifacts, "ROOT", repo)
    monkeypatch.setattr(security_artifacts, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(security_artifacts, "current_key", lambda strict=False: b"unit-test-key")
    monkeypatch.setattr(security_artifacts, "sign_file", lambda path, key: "bad-signature")
    monkeypatch.setattr(security_artifacts, "verify_file", lambda path, sig, key: False)

    with pytest.raises(ValueError, match="sbom signature verification failed immediately after generation"):
        security_artifacts.main()
