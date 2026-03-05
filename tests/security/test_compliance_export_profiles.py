from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, verify_file
from tooling.security import compliance_export_profiles


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_compliance_export_profiles_writes_signed_filtered_bundle(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _write(sec / "security_super_gate.json", {"status": "PASS"})
    _write(sec / "policy_signature_gate.json", {"status": "PASS"})
    _write(sec / "security_event_schema_gate.json", {"status": "PASS"})
    policy = repo / "governance" / "security" / "compliance_export_profiles.json"
    labels = repo / "governance" / "security" / "artifact_classification_manifest.json"
    _write(
        policy,
        {
            "profiles": {
                "soc2_like": {
                    "artifacts": [
                        "evidence/security/security_super_gate.json",
                        "evidence/security/policy_signature_gate.json",
                        "evidence/security/security_event_schema_gate.json",
                    ]
                }
            }
        },
    )
    _write(
        labels,
        {
            "artifacts": [
                {"path": "evidence/security/security_super_gate.json", "classification": "internal"},
                {"path": "evidence/security/policy_signature_gate.json", "classification": "internal"},
                {"path": "evidence/security/security_event_schema_gate.json", "classification": "internal"},
            ]
        },
    )

    monkeypatch.setattr(compliance_export_profiles, "ROOT", repo)
    monkeypatch.setattr(compliance_export_profiles, "POLICY", policy)
    monkeypatch.setattr(compliance_export_profiles, "CLASSIFICATION_MANIFEST", labels)
    monkeypatch.setattr(compliance_export_profiles, "evidence_root", lambda: repo / "evidence")

    assert compliance_export_profiles.main(["--profile", "soc2_like"]) == 0
    manifest = repo / "evidence" / "security" / "compliance_exports" / "soc2_like" / "export_manifest.json"
    sig = manifest.with_suffix(".json.sig")
    assert manifest.exists()
    assert sig.exists()
    assert verify_file(manifest, sig.read_text(encoding="utf-8").strip(), key=current_key(strict=False))


def test_compliance_export_profiles_fails_when_required_artifact_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _write(sec / "security_super_gate.json", {"status": "PASS"})
    policy = repo / "governance" / "security" / "compliance_export_profiles.json"
    labels = repo / "governance" / "security" / "artifact_classification_manifest.json"
    _write(
        policy,
        {
            "profiles": {
                "iso_like": {
                    "artifacts": [
                        "evidence/security/security_super_gate.json",
                        "evidence/security/missing.json",
                    ]
                }
            }
        },
    )
    _write(
        labels,
        {
            "artifacts": [
                {"path": "evidence/security/security_super_gate.json", "classification": "internal"},
                {"path": "evidence/security/missing.json", "classification": "internal"},
            ]
        },
    )

    monkeypatch.setattr(compliance_export_profiles, "ROOT", repo)
    monkeypatch.setattr(compliance_export_profiles, "POLICY", policy)
    monkeypatch.setattr(compliance_export_profiles, "CLASSIFICATION_MANIFEST", labels)
    monkeypatch.setattr(compliance_export_profiles, "evidence_root", lambda: repo / "evidence")

    assert compliance_export_profiles.main(["--profile", "iso_like"]) == 1
    report = json.loads((sec / "compliance_export_profiles.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("missing_artifact:") for item in report["findings"])


def test_compliance_export_profiles_fails_when_artifact_lacks_classification_label(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _write(sec / "security_super_gate.json", {"status": "PASS"})
    policy = repo / "governance" / "security" / "compliance_export_profiles.json"
    labels = repo / "governance" / "security" / "artifact_classification_manifest.json"
    _write(
        policy,
        {"profiles": {"soc2_like": {"artifacts": ["evidence/security/security_super_gate.json"]}}},
    )
    _write(labels, {"artifacts": []})

    monkeypatch.setattr(compliance_export_profiles, "ROOT", repo)
    monkeypatch.setattr(compliance_export_profiles, "POLICY", policy)
    monkeypatch.setattr(compliance_export_profiles, "CLASSIFICATION_MANIFEST", labels)
    monkeypatch.setattr(compliance_export_profiles, "evidence_root", lambda: repo / "evidence")

    assert compliance_export_profiles.main(["--profile", "soc2_like"]) == 1
    report = json.loads((sec / "compliance_export_profiles.json").read_text(encoding="utf-8"))
    assert "missing_artifact_classification_label:evidence/security/security_super_gate.json" in report["findings"]
