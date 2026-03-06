from __future__ import annotations

import json
from pathlib import Path

from tooling.security import attestation_index_signed_artifacts_gate


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_attestation_index_signed_artifacts_gate_passes_with_lane_requirements(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    gov = repo / "governance" / "security"
    sec.mkdir(parents=True)
    gov.mkdir(parents=True)

    _write(
        gov / "attestation_index_signed_artifacts_policy.json",
        {
            "default_required_signed_artifacts": ["evidence/security/policy_signature.json"],
            "lane_required_signed_artifacts": {
                "security-maintenance": [
                    "evidence/security/policy_signature.json",
                    "evidence/security/provenance_signature.json",
                ]
            },
        },
    )
    _write(
        sec / "evidence_attestation_index.json",
        {
            "items": [
                {"path": "evidence/security/policy_signature.json"},
                {"path": "evidence/security/provenance_signature.json"},
            ]
        },
    )

    monkeypatch.setattr(attestation_index_signed_artifacts_gate, "ROOT", repo)
    monkeypatch.setattr(
        attestation_index_signed_artifacts_gate,
        "POLICY",
        gov / "attestation_index_signed_artifacts_policy.json",
    )
    monkeypatch.setattr(attestation_index_signed_artifacts_gate, "evidence_root", lambda: repo / "evidence")

    assert attestation_index_signed_artifacts_gate.main(["--lane", "security-maintenance"]) == 0
    report = json.loads((sec / "attestation_index_signed_artifacts_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["summary"]["lane"] == "security-maintenance"


def test_attestation_index_signed_artifacts_gate_fails_on_missing_lane_artifact(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    gov = repo / "governance" / "security"
    sec.mkdir(parents=True)
    gov.mkdir(parents=True)

    _write(
        gov / "attestation_index_signed_artifacts_policy.json",
        {
            "default_required_signed_artifacts": ["evidence/security/policy_signature.json"],
            "lane_required_signed_artifacts": {
                "security-matrix": [
                    "evidence/security/policy_signature.json",
                    "evidence/security/provenance_signature.json",
                ]
            },
        },
    )
    _write(sec / "evidence_attestation_index.json", {"items": [{"path": "evidence/security/policy_signature.json"}]})

    monkeypatch.setattr(attestation_index_signed_artifacts_gate, "ROOT", repo)
    monkeypatch.setattr(
        attestation_index_signed_artifacts_gate,
        "POLICY",
        gov / "attestation_index_signed_artifacts_policy.json",
    )
    monkeypatch.setattr(attestation_index_signed_artifacts_gate, "evidence_root", lambda: repo / "evidence")

    assert attestation_index_signed_artifacts_gate.main(["--lane", "security-matrix"]) == 1
    report = json.loads((sec / "attestation_index_signed_artifacts_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert "missing_attestation_index_signed_artifact:security-matrix:evidence/security/provenance_signature.json" in report[
        "findings"
    ]
