from __future__ import annotations

import json
from pathlib import Path

from tooling.security import (
    dependency_trust_gate,
    provenance_witness_quorum_gate,
    transparency_log_export,
    transparency_log_gate,
)

ROOT = Path(__file__).resolve().parents[2]


def test_stage_s_gates_are_wired_into_super_gate() -> None:
    text = (ROOT / "tooling" / "security" / "security_super_gate.py").read_text(encoding="utf-8")
    expected = [
        "crypto_agility_matrix_gate.py",
        "provenance_witness_quorum_gate.py",
        "transparency_log_export.py",
        "transparency_log_gate.py",
        "time_source_attestation_gate.py",
        "build_environment_drift_gate.py",
        "artifact_classification_gate.py",
        "deterministic_redaction_gate.py",
        "disaster_recovery_drill_gate.py",
        "key_compromise_dual_control_gate.py",
        "dependency_trust_gate.py",
    ]
    for item in expected:
        assert item in text


def test_stage_s_policy_is_signature_managed() -> None:
    manifest = json.loads(
        (ROOT / "governance" / "security" / "policy_signature_manifest.json").read_text(encoding="utf-8")
    )
    policies = manifest.get("policies", [])
    assert "governance/security/stage_s_hardening_policy.json" in policies
    assert "governance/security/artifact_classification_manifest.json" in policies
    assert "governance/security/build_env_baseline.json" in policies


def test_provenance_witness_quorum_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "evidence" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "stage_s_hardening_policy.json").write_text(
        json.dumps(
            {
                "provenance_witness": {
                    "witness_file": "evidence/security/provenance_witnesses.json",
                    "minimum_unique_witnesses": 2,
                    "minimum_unique_roles": 2,
                }
            }
        ),
        encoding="utf-8",
    )
    (repo / "evidence" / "security" / "provenance_witnesses.json").write_text(
        json.dumps(
            {
                "witnesses": [
                    {"witness_id": "a", "role": "sec"},
                    {"witness_id": "b", "role": "rel"},
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        provenance_witness_quorum_gate,
        "load_stage_s_policy",
        lambda: {
            "provenance_witness": {
                "witness_file": "evidence/security/provenance_witnesses.json",
                "minimum_unique_witnesses": 2,
                "minimum_unique_roles": 2,
            }
        },
    )
    monkeypatch.setattr(provenance_witness_quorum_gate, "ROOT", repo)
    monkeypatch.setattr(provenance_witness_quorum_gate, "evidence_root", lambda: repo / "evidence")
    assert provenance_witness_quorum_gate.main([]) == 0


def test_transparency_log_export_and_gate(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "evidence" / "security").mkdir(parents=True)
    for name in ["sbom.json", "build_provenance.json", "slsa_provenance_v1.json"]:
        (repo / "evidence" / "security" / name).write_text('{"status":"PASS"}\n', encoding="utf-8")
    (repo / "governance" / "security" / "stage_s_hardening_policy.json").write_text(
        json.dumps(
            {
                "transparency_log": {
                    "log_path": "evidence/security/transparency_log.json",
                    "tracked_paths": [
                        "evidence/security/sbom.json",
                        "evidence/security/build_provenance.json",
                    ],
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        transparency_log_export,
        "load_stage_s_policy",
        lambda: {
            "transparency_log": {
                "log_path": "evidence/security/transparency_log.json",
                "tracked_paths": [
                    "evidence/security/sbom.json",
                    "evidence/security/build_provenance.json",
                ],
            }
        },
    )
    monkeypatch.setattr(
        transparency_log_gate,
        "load_stage_s_policy",
        lambda: {
            "transparency_log": {
                "log_path": "evidence/security/transparency_log.json",
                "tracked_paths": [
                    "evidence/security/sbom.json",
                    "evidence/security/build_provenance.json",
                ],
            }
        },
    )
    monkeypatch.setattr(transparency_log_export, "ROOT", repo)
    monkeypatch.setattr(transparency_log_export, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(transparency_log_gate, "ROOT", repo)
    monkeypatch.setattr(transparency_log_gate, "evidence_root", lambda: repo / "evidence")
    assert transparency_log_export.main([]) == 0
    assert transparency_log_gate.main([]) == 0


def test_dependency_trust_gate_passes_for_allowlisted_owners(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "evidence").mkdir(parents=True)
    (repo / ".github" / "workflows").mkdir(parents=True)
    (repo / ".github" / "workflows" / "ci.yml").write_text(
        "steps:\n  - uses: actions/checkout@abc\n  - uses: github/codeql-action/upload-sarif@abc\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        dependency_trust_gate,
        "load_stage_s_policy",
        lambda: {
            "dependency_trust": {
                "allowed_action_owners": ["actions", "github"],
                "allow_local_actions": True,
            }
        },
    )
    monkeypatch.setattr(dependency_trust_gate, "ROOT", repo)
    monkeypatch.setattr(dependency_trust_gate, "evidence_root", lambda: repo / "evidence")
    assert dependency_trust_gate.main([]) == 0
