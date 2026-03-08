from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import compliance_profile_artifact_gate


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sign(path: Path) -> None:
    path.with_suffix(".json.sig").write_text(sign_file(path, key=current_key(strict=False)) + "\n", encoding="utf-8")


def test_compliance_profile_artifact_gate_passes_when_all_required_artifacts_exported(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    evidence = repo / "evidence" / "security"
    policy = repo / "governance" / "security" / "compliance_export_profiles.json"
    _write(
        policy,
        {
            "profiles": {
                "soc2_like": {
                    "artifacts": [
                        "evidence/security/security_super_gate.json",
                        "evidence/security/policy_signature_gate.json",
                    ]
                }
            }
        },
    )
    manifest = evidence / "compliance_exports" / "soc2_like" / "export_manifest.json"
    _write(
        manifest,
        {
            "profile": "soc2_like",
            "copied_artifacts": [
                "evidence/security/security_super_gate.json",
                "evidence/security/policy_signature_gate.json",
            ],
        },
    )
    _sign(manifest)

    monkeypatch.setattr(compliance_profile_artifact_gate, "ROOT", repo)
    monkeypatch.setattr(compliance_profile_artifact_gate, "POLICY", policy)
    monkeypatch.setattr(compliance_profile_artifact_gate, "evidence_root", lambda: repo / "evidence")
    assert compliance_profile_artifact_gate.main([]) == 0


def test_compliance_profile_artifact_gate_fails_when_profile_bundle_missing_required_artifact(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    evidence = repo / "evidence" / "security"
    policy = repo / "governance" / "security" / "compliance_export_profiles.json"
    _write(
        policy,
        {
            "profiles": {
                "iso_like": {
                    "artifacts": [
                        "evidence/security/security_super_gate.json",
                        "evidence/security/security_retention_policy_gate.json",
                    ]
                }
            }
        },
    )
    manifest = evidence / "compliance_exports" / "iso_like" / "export_manifest.json"
    _write(manifest, {"profile": "iso_like", "copied_artifacts": ["evidence/security/security_super_gate.json"]})
    _sign(manifest)

    monkeypatch.setattr(compliance_profile_artifact_gate, "ROOT", repo)
    monkeypatch.setattr(compliance_profile_artifact_gate, "POLICY", policy)
    monkeypatch.setattr(compliance_profile_artifact_gate, "evidence_root", lambda: repo / "evidence")
    assert compliance_profile_artifact_gate.main([]) == 1
    report = json.loads((evidence / "compliance_profile_artifact_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("missing_required_profile_artifact:iso_like:") for item in report["findings"])
