from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_release_workflow_enforces_signature_verification() -> None:
    release = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    assert "verify-signatures:" in release
    assert "python tooling/security/provenance_signature_gate.py --strict-key" in release
    assert "python tooling/security/policy_signature_gate.py --strict-key" in release
    assert "python tooling/security/python_version_policy_gate.py" in release
    assert "python tooling/security/slsa_attestation_gate.py" in release
    assert "python tooling/security/org_secret_backend_gate.py" in release
    assert "python tooling/security/secret_management_gate.py" in release
    assert "python tooling/security/secret_origin_inventory_gate.py" in release
    assert "python tooling/security/secret_rotation_metadata_gate.py" in release
    assert "python tooling/security/stale_secret_usage_wiring_gate.py" in release
    assert "python tooling/security/break_glass_secret_usage_gate.py" in release
    assert "python tooling/security/offline_network_call_guard_gate.py" in release
    assert "python tooling/security/production_controls_gate.py" in release
    assert "python tooling/security/third_party_pentest_gate.py --strict-key" in release
    assert "python tooling/security/post_incident_closure_gate.py" in release
    assert "python tooling/security/docs_security_command_guard_gate.py" in release
    assert "python tooling/security/docs_snippet_pinning_gate.py" in release
    assert "python tooling/security/live_rollout_gate.py" in release
    assert "python tooling/security/container_provenance_gate.py" in release
    assert "python tooling/security/container_registry_provenance_gate.py" in release
    assert "python tooling/security/attestation_digest_match_gate.py" in release
    assert "python tooling/security/deploy_artifact_drift_gate.py" in release
    assert "python tooling/security/required_control_condition_bypass_gate.py" in release
    assert "python tooling/security/strict_lane_fail_closed_control_gate.py" in release
    assert "python tooling/security/warning_lane_degraded_mode_artifact_gate.py" in release
    assert "python tooling/security/workflow_change_management_gate.py" in release
    assert "python tooling/security/stale_policy_review_gate.py" in release
    assert "python tooling/security/policy_deprecation_gate.py" in release
    assert "python tooling/security/ownership_continuity_gate.py" in release
    assert "python tooling/security/threat_control_mapping_gate.py" in release
    assert "python tooling/security/audit_archive_verify.py" in release
    assert "python tooling/security/artifact_path_case_conflict_gate.py" in release
    assert "python tooling/security/abuse_telemetry_snapshot.py" in release
    assert "python tooling/security/abuse_telemetry_gate.py" in release
    assert "python tooling/security/expired_degraded_mode_allowance_gate.py" in release
    assert "python tooling/security/exception_path_metadata_gate.py" in release
    assert "python tooling/security/degraded_mode_evidence.py" in release
    assert "python tooling/security/emergency_lockdown_gate.py" in release
    assert "python tooling/security/exception_waiver_reconciliation_gate.py" in release
    assert "python tooling/security/exception_waiver_unique_id_gate.py" in release
    assert "python tooling/security/promotion_policy_gate.py" in release
    assert "python tooling/security/security_state_transition_invariants_gate.py" in release
    assert "python tooling/security/canary_promotion_guard.py" in release
    assert "python tooling/security/incident_regression_catalog_gate.py" in release
    assert "python tooling/security/high_severity_incident_regression_gate.py" in release
    assert "python tooling/security/ci_failure_classifier.py" in release
    assert "python tooling/security/evidence_attestation_index.py --strict-key" in release
    assert "python tooling/security/attestation_index_signed_artifacts_gate.py --lane release-verify" in release
    assert "python tooling/security/evidence_attestation_gate.py --strict-key" in release
    assert "python tooling/security/key_provenance_continuity_gate.py" in release
    assert "python tooling/security/key_usage_ledger.py" in release
    assert "python tooling/security/strict_release_fallback_key_indicator_gate.py" in release
    assert "python tooling/security/release_strict_key_mode_gate.py" in release
    assert "python tooling/security/release_evidence_root_isolation_gate.py" in release
    assert "python tooling/security/release_publish_rollback_order_gate.py" in release
    assert "python tooling/security/workflow_evidence_scope_gate.py" in release
    assert "python tooling/security/external_action_owner_allowlist_gate.py" in release
    assert "python tooling/security/third_party_action_sha_mapping_gate.py" in release
    assert "python tooling/security/conformance_security_coupling_gate.py" in release
    assert "python tooling/security/security_super_gate.py --strict-key" in release
    assert "python tooling/security/security_gate_runtime_budget_gate.py" in release
    assert "python tooling/security/deploy_decision_record.py" in release
    assert "python tooling/security/rolling_merkle_checkpoints.py" in release
    assert "python tooling/security/merkle_checkpoint_continuity_gate.py" in release
    assert "python tooling/security/tamper_cost_model_report.py" in release
    assert "python tooling/security/upload_artifact_immutable_index.py" in release
    assert "python tooling/security/security_event_export.py" in release
    assert "python tooling/security/security_event_schema_gate.py" in release
    assert "python tooling/security/telemetry_completeness_sli_gate.py" in release
    assert "python tooling/security/telemetry_timeliness_sli_gate.py" in release
    assert "python tooling/security/telemetry_integrity_sli_gate.py" in release
    assert "python tooling/security/security_pipeline_reliability_dashboard.py" in release
    assert "python tooling/security/security_posture_executive_summary.py" in release
    assert "python tooling/security/formal_security_review_artifact.py --strict-key" in release
    assert "python tooling/security/live_rollout_gate.py --profile release" in release
    assert "canary_promotion_guard.json" in release
    assert "degraded_mode_evidence.json" in release
    assert "exception_path_metadata_gate.json" in release
    assert "python_version_policy_gate.json" in release
    assert "secret_origin_inventory_gate.json" in release
    assert "secret_rotation_metadata_gate.json" in release
    assert "stale_secret_usage_wiring_gate.json" in release
    assert "break_glass_secret_usage_gate.json" in release
    assert "offline_network_call_guard_gate.json" in release
    assert "deploy_artifact_drift_gate.json" in release
    assert "required_control_condition_bypass_gate.json" in release
    assert "docs_security_command_guard_gate.json" in release
    assert "docs_snippet_pinning_gate.json" in release
    assert "strict_lane_fail_closed_control_gate.json" in release
    assert "warning_lane_degraded_mode_artifact_gate.json" in release
    assert "workflow_change_management_gate.json" in release
    assert "policy_deprecation_gate.json" in release
    assert "ownership_continuity_gate.json" in release
    assert "deploy_decision_record.json" in release
    assert "deploy_decision_record.json.sig" in release
    assert "deploy_decision_record_gate.json" in release
    assert "external_action_owner_allowlist_gate.json" in release
    assert "third_party_action_sha_mapping_gate.json" in release
    assert "incident_regression_catalog_gate.json" in release
    assert "high_severity_incident_regression_gate.json" in release
    assert "ci_failure_classifier.json" in release
    assert "ci_failure_classifier_history.json" in release
    assert "artifact_path_case_conflict_gate.json" in release
    assert "expired_degraded_mode_allowance_gate.json" in release
    assert "exception_waiver_unique_id_gate.json" in release
    assert "rolling_merkle_checkpoints.json" in release
    assert "rolling_merkle_checkpoints.json.sig" in release
    assert "rolling_merkle_checkpoints_gate.json" in release
    assert "security_gate_runtime_budget_gate.json" in release
    assert "security_gate_runtime_history.json" in release
    assert "tamper_cost_model_report.json" in release
    assert "upload_artifact_immutable_index.json" in release
    assert "upload_artifact_immutable_index.json.sig" in release
    assert "telemetry_completeness_sli_gate.json" in release
    assert "telemetry_timeliness_sli_gate.json" in release
    assert "telemetry_integrity_sli_gate.json" in release
    assert "telemetry_integrity_trend_alert.json" in release
    assert "security_state_transition_invariants_gate.json" in release
    assert "key_provenance_continuity_gate.json" in release
    assert "key_usage_ledger.json" in release
    assert "strict_release_fallback_key_indicator_gate.json" in release
    assert "release_strict_key_mode_gate.json" in release
    assert "release_evidence_root_isolation_gate.json" in release
    assert "release_publish_rollback_order_gate.json" in release
    assert "attestation_index_signed_artifacts_gate.json" in release
    assert "security_pipeline_reliability_dashboard.json" in release
    assert "security_pipeline_reliability_history.json" in release
    assert "security_posture_executive_summary.json" in release
    assert "formal_security_review_artifact.json" in release
    assert "formal_security_review_artifact.json.sig" in release
    assert "steps.merkle_build_root.outputs.root" in release
    assert "GLYPHSER_EXPECTED_PREVIOUS_MERKLE_ROOT" in release
    assert "GLYPHSER_EVIDENCE_ROOT: evidence/runs/${{ github.run_id }}/release-build" in release
    assert "GLYPHSER_EVIDENCE_ROOT: evidence/runs/${{ github.run_id }}/release-verify" in release
    assert "GLYPHSER_EVIDENCE_ROOT: evidence/runs/${{ github.run_id }}/release-publish" in release
    assert "python tooling/security/evidence_run_dir_guard.py --run-id" in release
    assert 'GLYPHSER_CONTAINER_PUBLISHING_ENABLED: "true"' in release
    assert 'GLYPHSER_STRICT_SIGNING: "true"' in release
    assert "GLYPHSER_PROVENANCE_HMAC_KEY: ${{ secrets.GLYPHSER_PROVENANCE_HMAC_KEY }}" in release
    assert "python tooling/security/release_publish_artifact_presence_gate.py --artifact-root . --run-id" in release


def test_release_workflow_avoids_unpinned_action_tags() -> None:
    release = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    assert "actions/download-artifact@fa0a91b85d4f404e444e00e005971372dc801d16" in release
    assert "actions/download-artifact@v" not in release
    assert "gh-action-pypi-publish@" not in release
