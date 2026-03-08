from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import verify_file
from tooling.security import export_offline_verify_bundle


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_required_inputs(repo: Path) -> None:
    _write(repo / "governance" / "security" / "policy_signature_manifest.json", '{"policies":[]}\n')
    _write(repo / "governance" / "security" / "policy_signature_manifest.json.sig", "sig\n")
    _write(repo / "governance" / "security" / "provenance_revocation_list.json", '{"revocations":[]}\n')
    _write(repo / "governance" / "security" / "provenance_revocation_list.json.sig", "sig\n")
    _write(repo / "evidence" / "security" / "build_provenance.json", '{"status":"ok"}\n')
    _write(repo / "evidence" / "security" / "build_provenance.json.sig", "sig\n")
    _write(repo / "evidence" / "security" / "sbom.json", '{"packages":[]}\n')
    _write(repo / "evidence" / "security" / "sbom.json.sig", "sig\n")
    _write(repo / "evidence" / "security" / "evidence_chain_of_custody.json", '{"items":[]}\n')
    _write(repo / "evidence" / "security" / "evidence_chain_of_custody.json.sig", "sig\n")


def test_export_offline_verify_bundle_exports_signed_pairs(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_required_inputs(repo)

    monkeypatch.setattr(export_offline_verify_bundle, "ROOT", repo)
    monkeypatch.setattr(export_offline_verify_bundle, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        export_offline_verify_bundle,
        "load_policy",
        lambda: {"offline_bundle_dir": "evidence/security/offline_verify_bundle"},
    )

    assert export_offline_verify_bundle.main([]) == 0
    bundle = repo / "evidence" / "security" / "offline_verify_bundle"
    assert (bundle / "policy_signature_manifest.json.sig").exists()
    assert (bundle / "provenance_revocation_list.json.sig").exists()
    assert (bundle / "build_provenance.json.sig").exists()
    assert (bundle / "sbom.json.sig").exists()
    assert (bundle / "evidence_chain_of_custody.json.sig").exists()
    manifest = bundle / "export_manifest.json"
    manifest_sig = bundle / "export_manifest.json.sig"
    assert manifest.exists()
    assert manifest_sig.exists()
    assert verify_file(manifest, manifest_sig.read_text(encoding="utf-8").strip(), key=b"glyphser-provenance-hmac-fallback-v1")
    manifest_payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert manifest_payload["api_contract_version"] == "v1"
    report = json.loads((repo / "evidence" / "security" / "offline_verify_bundle_export.json").read_text(encoding="utf-8"))
    assert report["metadata"]["api_contract_version"] == "v1"
    assert "offline_verify.py" in (bundle / "VERIFY.txt").read_text(encoding="utf-8")


def test_export_offline_verify_bundle_fails_on_missing_signature(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_required_inputs(repo)
    (repo / "evidence" / "security" / "sbom.json.sig").unlink()

    monkeypatch.setattr(export_offline_verify_bundle, "ROOT", repo)
    monkeypatch.setattr(export_offline_verify_bundle, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        export_offline_verify_bundle,
        "load_policy",
        lambda: {"offline_bundle_dir": "evidence/security/offline_verify_bundle"},
    )

    assert export_offline_verify_bundle.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "offline_verify_bundle_export.json").read_text("utf-8"))
    assert any("missing_source:" in item and "sbom.json.sig" in item for item in report["findings"])
