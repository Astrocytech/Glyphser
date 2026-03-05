from __future__ import annotations

import json
from pathlib import Path

from tooling.security import (
    deterministic_env_gate,
    exception_registry_gate,
    sbom_diff_review_gate,
)

ROOT = Path(__file__).resolve().parents[2]


def test_super_gate_references_new_post_qr_gates() -> None:
    text = (ROOT / "tooling" / "security" / "security_super_gate.py").read_text(encoding="utf-8")
    expected = [
        "security_workflow_evidence_bundle_gate.py",
        "replay_abuse_regression_gate.py",
        "exception_registry_gate.py",
        "lockdown_blast_radius_gate.py",
        "canonical_json_roundtrip_gate.py",
        "file_permission_matrix_gate.py",
        "tamper_canary_gate.py",
        "security_docs_traceability_gate.py",
        "sbom_diff_review_gate.py",
        "egress_policy_gate.py",
        "attestation_freshness_gate.py",
        "crypto_algorithm_policy_gate.py",
        "split_duty_gate.py",
        "export_offline_verify_bundle.py",
        "dependency_confusion_gate.py",
        "deterministic_env_gate.py",
        "archive_integrity_revalidation_gate.py",
        "compromised_runner_drill.py",
        "governance_compliance_delta_report.py",
        "governance_compliance_quarterly_snapshot.py",
        "gate_status_transition_anomaly_detector.py",
        "cross_run_suspicious_pattern_linkage_gate.py",
        "containment_auto_trigger_recommendations.py",
        "incident_severity_scoring_report.py",
        "evidence_notarization_checkpoint.py",
        "manifest_pointer_meta_chain.py",
        "archival_encryption_verification_gate.py",
        "quarterly_restore_simulation.py",
        "developer_mode_profile_gate.py",
        "promotion_go_no_go_report.py",
        "signed_promotion_decision_artifact.py",
        "release_notes_security_status_gate.py",
        "release_metadata_evidence_checksum.py",
        "lockfile_transitive_provenance_gate.py",
        "toolchain_binary_source_consistency_gate.py",
        "package_metadata_anomaly_gate.py",
        "mirrored_source_integrity_report.py",
        "chaos_security_scenario_report.py",
        "gate_retry_strategy_policy_gate.py",
        "branch_protection_policy_gate.py",
        "codeowners_security_coverage_gate.py",
        "permissions_audit_artifact.py",
        "emergency_access_review_gate.py",
    ]
    for item in expected:
        assert item in text


def test_policy_manifest_contains_new_signed_documents() -> None:
    payload = json.loads(
        (ROOT / "governance" / "security" / "policy_signature_manifest.json").read_text(encoding="utf-8")
    )
    policies = payload.get("policies", [])
    assert "governance/security/advanced_hardening_policy.json" in policies
    assert "governance/security/temporary_exceptions.json" in policies
    assert "governance/security/sbom_diff_approval.json" in policies


def test_tamper_canary_workflow_exists() -> None:
    wf = (ROOT / ".github" / "workflows" / "security-tamper-canary.yml").read_text(encoding="utf-8")
    assert "tamper_canary_gate.py" in wf
    assert "workflow_dispatch" in wf
    assert "schedule:" in wf


def test_local_ci_security_repro_docs_exist() -> None:
    doc = (ROOT / "governance" / "security" / "LOCAL_CI_SECURITY_REPRO.md").read_text(encoding="utf-8")
    assert "security_super_gate.py --strict-prereqs --strict-key" in doc
    assert "GLYPHSER_MOCK_ATTESTATIONS" in doc
    assert "TZ=UTC" in doc


def test_semgrep_rules_tests_are_not_skip_marked() -> None:
    text = (ROOT / "tests" / "security" / "test_semgrep_rules.py").read_text(encoding="utf-8")
    assert "skipif" not in text


def test_exception_registry_gate_passes_for_empty_registry(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "evidence").mkdir(parents=True)
    (repo / "governance" / "security" / "advanced_hardening_policy.json").write_text(
        json.dumps(
            {
                "exception_registry_path": "governance/security/temporary_exceptions.json",
                "max_active_exceptions": 2,
            }
        ),
        encoding="utf-8",
    )
    (repo / "governance" / "security" / "temporary_exceptions.json").write_text(
        '{"exceptions": []}\n',
        encoding="utf-8",
    )

    monkeypatch.setattr(exception_registry_gate, "ROOT", repo)
    monkeypatch.setattr(exception_registry_gate, "evidence_root", lambda: repo / "evidence")
    assert exception_registry_gate.main([]) == 0


def test_deterministic_env_gate_non_ci_mode(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "evidence").mkdir(parents=True)
    (repo / "governance" / "security" / "advanced_hardening_policy.json").write_text(
        json.dumps({"required_env_vars": ["TZ", "LC_ALL", "LANG"], "required_timezone": "UTC"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(deterministic_env_gate, "ROOT", repo)
    monkeypatch.setattr(deterministic_env_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.delenv("CI", raising=False)
    assert deterministic_env_gate.main([]) == 0


def test_sbom_diff_review_gate_bootstrap_without_previous(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "evidence" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "advanced_hardening_policy.json").write_text(
        json.dumps(
            {
                "sbom_current_path": "evidence/security/sbom.json",
                "sbom_previous_path": "evidence/security/sbom.previous.json",
                "sbom_diff_approval_path": "governance/security/sbom_diff_approval.json",
            }
        ),
        encoding="utf-8",
    )
    (repo / "evidence" / "security" / "sbom.json").write_text('{"packages": []}\n', encoding="utf-8")
    (repo / "governance" / "security" / "sbom_diff_approval.json").write_text(
        '{"allowed_changes": []}\n',
        encoding="utf-8",
    )

    monkeypatch.setattr(sbom_diff_review_gate, "ROOT", repo)
    monkeypatch.setattr(sbom_diff_review_gate, "evidence_root", lambda: repo / "evidence")
    assert sbom_diff_review_gate.main([]) == 0
