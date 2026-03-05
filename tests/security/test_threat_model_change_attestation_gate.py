from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import threat_model_change_attestation_gate


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _matrix() -> dict:
    return {
        "controls": [
            {
                "id": "CTRL-PROVENANCE-SIGNATURE",
                "gates": ["tooling/security/policy_signature_gate.py"],
            },
            {
                "id": "CTRL-LOW-RISK",
                "gates": ["tooling/security/review_policy_gate.py"],
            },
        ],
        "critical_gates": ["tooling/security/policy_signature_gate.py"],
    }


def test_threat_model_change_attestation_gate_skips_when_no_critical_changes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    matrix = repo / "governance" / "security" / "threat_control_matrix.json"
    _write(matrix, _matrix())
    monkeypatch.setattr(threat_model_change_attestation_gate, "ROOT", repo)
    monkeypatch.setattr(threat_model_change_attestation_gate, "MATRIX", matrix)
    monkeypatch.setattr(
        threat_model_change_attestation_gate,
        "ATTESTATION",
        repo / "governance" / "security" / "metadata" / "THREAT_MODEL_CHANGE_ATTESTATION.json",
    )
    monkeypatch.setattr(threat_model_change_attestation_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(threat_model_change_attestation_gate, "_changed_control_ids", lambda: {"CTRL-LOW-RISK"})

    assert threat_model_change_attestation_gate.main([]) == 0


def test_threat_model_change_attestation_gate_fails_when_attestation_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    matrix = repo / "governance" / "security" / "threat_control_matrix.json"
    _write(matrix, _matrix())
    monkeypatch.setattr(threat_model_change_attestation_gate, "ROOT", repo)
    monkeypatch.setattr(threat_model_change_attestation_gate, "MATRIX", matrix)
    monkeypatch.setattr(
        threat_model_change_attestation_gate,
        "ATTESTATION",
        repo / "governance" / "security" / "metadata" / "THREAT_MODEL_CHANGE_ATTESTATION.json",
    )
    monkeypatch.setattr(threat_model_change_attestation_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(threat_model_change_attestation_gate, "_changed_control_ids", lambda: {"CTRL-PROVENANCE-SIGNATURE"})

    assert threat_model_change_attestation_gate.main([]) == 1


def test_threat_model_change_attestation_gate_passes_with_signed_attestation(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    matrix = repo / "governance" / "security" / "threat_control_matrix.json"
    _write(matrix, _matrix())
    att = repo / "governance" / "security" / "metadata" / "THREAT_MODEL_CHANGE_ATTESTATION.json"
    _write(
        att,
        {
            "status": "APPROVED",
            "changed_controls": ["CTRL-PROVENANCE-SIGNATURE"],
            "approvers": ["security-team"],
            "rationale": "critical control update",
        },
    )
    att.with_suffix(".json.sig").write_text(sign_file(att, key=current_key(strict=False)) + "\n", encoding="utf-8")

    monkeypatch.setattr(threat_model_change_attestation_gate, "ROOT", repo)
    monkeypatch.setattr(threat_model_change_attestation_gate, "MATRIX", matrix)
    monkeypatch.setattr(threat_model_change_attestation_gate, "ATTESTATION", att)
    monkeypatch.setattr(threat_model_change_attestation_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(threat_model_change_attestation_gate, "_changed_control_ids", lambda: {"CTRL-PROVENANCE-SIGNATURE"})

    assert threat_model_change_attestation_gate.main([]) == 0
