from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_federation_manifest


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_security_federation_manifest_writes_signed_manifest(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    ev = repo / "evidence"
    _write(repo / "governance" / "security" / "external_artifact_trust_contract.json", {"accepted_repositories": ["github.com/a"]})
    _write(repo / "governance" / "security" / "security_standards_profile.json", {"consumer_repos": ["glyphser-sdk-python"]})

    class _Signing:
        @staticmethod
        def current_key(strict: bool = False) -> str:
            _ = strict
            return "k"

        @staticmethod
        def sign_file(path: Path, *, key: str) -> str:
            _ = (path, key)
            return "sig"

    monkeypatch.setattr(security_federation_manifest, "ROOT", repo)
    monkeypatch.setattr(
        security_federation_manifest,
        "TRUST_CONTRACT",
        repo / "governance" / "security" / "external_artifact_trust_contract.json",
    )
    monkeypatch.setattr(
        security_federation_manifest,
        "STANDARDS_PROFILE",
        repo / "governance" / "security" / "security_standards_profile.json",
    )
    monkeypatch.setattr(security_federation_manifest, "artifact_signing", _Signing)
    monkeypatch.setattr(security_federation_manifest, "evidence_root", lambda: ev)

    assert security_federation_manifest.main([]) == 0
    report = json.loads((ev / "security" / "security_federation_manifest.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert (ev / "security" / "security_federation_manifest.json.sig").read_text(encoding="utf-8").strip() == "sig"
