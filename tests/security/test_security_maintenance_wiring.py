from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_security_maintenance_workflow_wired() -> None:
    wf = (ROOT / ".github" / "workflows" / "security-maintenance.yml").read_text(encoding="utf-8")
    assert "schedule:" in wf
    assert "concurrency:" in wf
    assert "cancel-in-progress: false" in wf
    assert "python tooling/security/dependency_refresh_report.py" in wf
    assert "python tooling/security/install_security_toolchain.py" in wf
    assert "python tooling/security/security_cache_integrity_gate.py" in wf
    assert "GLYPHSER_EVIDENCE_ROOT: evidence/runs/${{ github.run_id }}/security-maintenance" in wf
    assert "python tooling/security/evidence_run_dir_guard.py --run-id" in wf
    assert "python tooling/security/policy_signature_gate.py --strict-key" in wf
    assert "python tooling/security/policy_schema_validation_gate.py" in wf
    assert "python tooling/security/stochastic_seed_policy_gate.py" in wf
    assert "python tooling/security/security_schema_migration_tracker.py" in wf
    assert "python tooling/security/security_schema_strict_readiness_gate.py" in wf
    assert "python tooling/security/security_super_gate_manifest_gate.py" in wf
    assert "python tooling/security/workflow_artifact_retention_gate.py" in wf
    assert "python tooling/security/semgrep_rules_self_check_gate.py" in wf
    assert "python tooling/security/workflow_policy_coverage_gate.py" in wf
    assert "python tooling/security/scheduled_workflow_backpressure_gate.py" in wf
    assert "python tooling/security/security_evidence_corruption_gate.py" in wf
    assert "python tooling/security/security_artifact_signature_coverage_gate.py" in wf
    assert "python tooling/security/artifact_path_case_conflict_gate.py" in wf
    assert "python tooling/security/security_unsigned_json_gate.py" in wf
    assert "python tooling/security/threat_control_mapping_gate.py" in wf
    assert "python tooling/security/security_toolchain_gate.py" in wf
    assert "python tooling/security/toolchain_dependency_provenance_gate.py" in wf
    assert "python tooling/security/toolchain_source_failover_gate.py" in wf
    assert "python tooling/security/python_version_policy_gate.py" in wf
    assert "python tooling/security/workflow_risky_patterns_gate.py" in wf
    assert "python tooling/security/required_control_condition_bypass_gate.py" in wf
    assert "python tooling/security/strict_lane_fail_closed_control_gate.py" in wf
    assert "python tooling/security/warning_lane_degraded_mode_artifact_gate.py" in wf
    assert "python tooling/security/workflow_change_management_gate.py" in wf
    assert "python tooling/security/workflow_deprecated_invocation_gate.py" in wf
    assert "python tooling/security/subprocess_allowlist_report.py" in wf
    assert "python tooling/security/subprocess_direct_usage_gate.py" in wf
    assert "python tooling/security/pip_audit_gate.py" in wf
    assert "python tooling/security/dependency_freshness_gate.py" in wf
    assert "python tooling/security/dependency_registry_policy_gate.py" in wf
    assert "python tooling/security/lockfile_change_provenance_gate.py" in wf
    assert "python tooling/security/offline_vulnerability_snapshot_compare.py" in wf
    assert "python tooling/security/ci_incident_replay_harness.py" in wf
    assert "python tooling/security/temp_directory_policy_gate.py" in wf
    assert "python tooling/security/secret_scan_gate.py" in wf
    assert "python tooling/security/workflow_pinning_gate.py" in wf
    assert "python tooling/security/external_action_owner_allowlist_gate.py" in wf
    assert "python tooling/security/third_party_action_sha_mapping_gate.py" in wf
    assert "python tooling/security/incident_response_gate.py" in wf
    assert "python tooling/security/containment_verification_gate.py" in wf
    assert "python tooling/security/post_incident_closure_gate.py" in wf
    assert "python tooling/security/org_secret_backend_gate.py" in wf
    assert "python tooling/security/secret_management_gate.py" in wf
    assert "python tooling/security/secret_origin_inventory_gate.py" in wf
    assert "python tooling/security/secret_rotation_metadata_gate.py" in wf
    assert "python tooling/security/stale_secret_usage_wiring_gate.py" in wf
    assert "python tooling/security/break_glass_secret_usage_gate.py" in wf
    assert "python tooling/security/offline_network_call_guard_gate.py" in wf
    assert "python tooling/security/production_controls_gate.py" in wf
    assert "python tooling/security/third_party_pentest_gate.py --strict-key" in wf
    assert "python tooling/security/live_integrations_verify.py" in wf
    assert "GLYPHSER_WAF_HEALTH_URL" in wf
    assert "python tooling/security/live_rollout_gate.py --target live_integrations" in wf
    assert "python tooling/security/container_provenance_gate.py" in wf
    assert "python tooling/security/abuse_telemetry_snapshot.py" in wf
    assert "python tooling/security/runtime_api_state_schema_gate.py" in wf
    assert "python tooling/security/runtime_api_input_surface_gate.py" in wf
    assert "python tooling/security/runtime_api_scope_matrix_gate.py" in wf
    assert "python tooling/security/fallback_secret_usage_gate.py" in wf
    assert "python tooling/security/abuse_telemetry_gate.py" in wf
    assert "python tooling/security/exception_path_metadata_gate.py" in wf
    assert "python tooling/security/degraded_mode_evidence.py" in wf
    assert "python tooling/security/evidence_attestation_index.py --strict-key" in wf
    assert "python tooling/security/evidence_attestation_gate.py --strict-key" in wf
    assert "python tooling/security/provenance_signature_gate.py --strict-key" in wf
    assert "python tooling/security/key_provenance_continuity_gate.py" in wf
    assert "python tooling/security/signature_algorithm_policy_gate.py" in wf
    assert "python tooling/security/security_verification_summary.py --strict-key" in wf
    assert "python tooling/security/slsa_attestation_gate.py" in wf
    assert "python tooling/security/workflow_evidence_scope_gate.py" in wf
    assert "python tooling/security/conformance_security_coupling_gate.py" in wf
    assert "python tooling/security/security_super_gate.py --strict-key" in wf
    assert "python tooling/security/security_gate_runtime_budget_gate.py" in wf
    assert "python tooling/security/incident_bundle_collect.py --incident-id" in wf
    assert "python tooling/security/tabletop_replay.py --bundle" in wf
    assert "python tooling/security/deterministic_replay_harness.py --run-dir" in wf
    assert "python tooling/security/replay_nondeterministic_field_drift_gate.py --run-dir" in wf
    assert "python tooling/security/replay_artifact_index.py --run-dir" in wf
    assert "airgap-simulation:" in wf
    assert "GLYPHSER_EVIDENCE_ROOT: evidence/runs/${{ github.run_id }}/airgap-simulation" in wf
    assert "python tooling/security/export_offline_verify_bundle.py" in wf
    assert "python tooling/security/offline_verify.py --bundle-dir evidence/security/offline_verify_bundle" in wf
    assert "python tooling/security/offline_verification_gate.py" in wf
    assert "python tooling/security/long_term_retention_manifest.py" in wf
    assert "python tooling/security/periodic_integrity_sampling.py" in wf
    assert "python tooling/security/security_event_export.py" in wf
    assert "python tooling/security/security_event_schema_gate.py" in wf
    assert "python tooling/security/telemetry_completeness_sli_gate.py" in wf
    assert "python tooling/security/telemetry_timeliness_sli_gate.py" in wf
    assert "python tooling/security/telemetry_integrity_sli_gate.py" in wf
    assert "python tooling/security/security_pipeline_reliability_dashboard.py" in wf
    assert "python tooling/security/security_posture_executive_summary.py" in wf
    assert "python tooling/security/formal_security_review_artifact.py --strict-key" in wf
    assert "python tooling/security/policy_review_freshness_gate.py" in wf
    assert "python tooling/security/policy_deprecation_gate.py" in wf
    assert "python tooling/security/ownership_continuity_gate.py" in wf
    assert "python tooling/security/signed_policy_metadata_gate.py" in wf
    assert "python tooling/security/approval_policy_violation_audit.py" in wf
    assert "python tooling/security/incident_regression_catalog_gate.py" in wf
    assert "python tooling/security/high_severity_incident_regression_gate.py" in wf
    assert "python tooling/security/ci_failure_classifier.py" in wf
    assert "python tooling/security/monthly_top_recurring_failures_report.py" in wf
    assert "python tooling/security/hardening_stale_ticket_gate.py" in wf
    assert "python tooling/security/top_risk_unresolved_items_ranker.py" in wf
    assert "python tooling/security/adversarial_campaign_plan_gate.py" in wf
    assert "python tooling/security/insider_threat_workflow_simulation.py" in wf
    assert "python tooling/security/artifact_omission_attack_simulation.py" in wf
    assert "python tooling/security/report_injection_mixture_simulation.py" in wf
    assert "python tooling/security/adversarial_resilience_scorecard.py" in wf
    assert "python tooling/security/recurring_failure_closure_gate.py" in wf
    assert "python tooling/security/security_workflow_trigger_gate.py" in wf
    assert "python tooling/security/security_critical_test_wiring_gate.py" in wf
    assert "security_workflow_contract_gate.json" in wf
    assert "workflow_risky_patterns_gate.json" in wf
    assert "required_control_condition_bypass_gate.json" in wf
    assert "strict_lane_fail_closed_control_gate.json" in wf
    assert "warning_lane_degraded_mode_artifact_gate.json" in wf
    assert "workflow_change_management_gate.json" in wf
    assert "workflow_deprecated_invocation_gate.json" in wf
    assert "subprocess_allowlist_report.json" in wf
    assert "subprocess_direct_usage_gate.json" in wf
    assert "policy_schema_validation_gate.json" in wf
    assert "stochastic_seed_policy_gate.json" in wf
    assert "security_schema_migration_tracker.json" in wf
    assert "security_schema_strict_readiness_gate.json" in wf
    assert "security_super_gate_manifest_gate.json" in wf
    assert "workflow_artifact_retention_gate.json" in wf
    assert "semgrep_rules_self_check_gate.json" in wf
    assert "workflow_policy_coverage_gate.json" in wf
    assert "scheduled_workflow_backpressure_gate.json" in wf
    assert "security_evidence_corruption_gate.json" in wf
    assert "security_artifact_signature_coverage_gate.json" in wf
    assert "artifact_path_case_conflict_gate.json" in wf
    assert "security_unsigned_json_gate.json" in wf
    assert "external_action_owner_allowlist_gate.json" in wf
    assert "third_party_action_sha_mapping_gate.json" in wf
    assert "python_version_policy_gate.json" in wf
    assert "security_toolchain_install_report.json" in wf
    assert "security_cache_integrity_gate.json" in wf
    assert "toolchain_dependency_provenance_gate.json" in wf
    assert "toolchain_source_failover_gate.json" in wf
    assert "toolchain_source_failover_history.json" in wf
    assert "dependency_freshness_gate.json" in wf
    assert "dependency_registry_policy_gate.json" in wf
    assert "lockfile_change_provenance_gate.json" in wf
    assert "offline_vulnerability_snapshot_compare.json" in wf
    assert "offline_vulnerability_snapshot_latest.json" in wf
    assert "ci_incident_replay_harness.json" in wf
    assert "temp_directory_policy_gate.json" in wf
    assert "policy_review_freshness_gate.json" in wf
    assert "policy_deprecation_gate.json" in wf
    assert "ownership_continuity_gate.json" in wf
    assert "signed_policy_metadata_gate.json" in wf
    assert "approval_policy_violation_audit.json" in wf
    assert "approval_policy_violation_audit_history.json" in wf
    assert "incident_regression_catalog_gate.json" in wf
    assert "high_severity_incident_regression_gate.json" in wf
    assert "ci_failure_classifier.json" in wf
    assert "ci_failure_classifier_history.json" in wf
    assert "monthly_top_recurring_failures_report.json" in wf
    assert "hardening_stale_ticket_gate.json" in wf
    assert "top_risk_unresolved_items_ranker.json" in wf
    assert "adversarial_campaign_plan_gate.json" in wf
    assert "insider_threat_workflow_simulation.json" in wf
    assert "artifact_omission_attack_simulation.json" in wf
    assert "report_injection_mixture_simulation.json" in wf
    assert "adversarial_resilience_scorecard.json" in wf
    assert "recurring_failure_closure_gate.json" in wf
    assert "threat_control_mapping_gate.json" in wf
    assert "security_workflow_trigger_gate.json" in wf
    assert "security_critical_test_wiring_gate.json" in wf
    assert "security_sarif_permissions_gate.json" in wf
    assert "security_workflow_permissions_policy_gate.json" in wf
    assert "security_exception_suppression_gate.json" in wf
    assert "security_dead_gate_wiring_gate.json" in wf
    assert "runtime_api_state_schema_gate.json" in wf
    assert "runtime_api_input_surface_gate.json" in wf
    assert "runtime_api_scope_matrix_gate.json" in wf
    assert "fallback_secret_usage_gate.json" in wf
    assert "exception_path_metadata_gate.json" in wf
    assert "degraded_mode_evidence.json" in wf
    assert "containment_verification_gate.json" in wf
    assert "post_incident_closure_gate.json" in wf
    assert "secret_origin_inventory_gate.json" in wf
    assert "secret_rotation_metadata_gate.json" in wf
    assert "stale_secret_usage_wiring_gate.json" in wf
    assert "break_glass_secret_usage_gate.json" in wf
    assert "offline_network_call_guard_gate.json" in wf
    assert "tabletop_replay.json" in wf
    assert "deterministic_replay_harness.json" in wf
    assert "replay_nondeterministic_field_drift_gate.json" in wf
    assert "replay_artifact_index.json" in wf
    assert "incident-bundle-${{ github.run_id }}.tar.gz" in wf
    assert "incident-bundle-${{ github.run_id }}.tar.gz.sha256" in wf
    assert "long_term_retention_manifest.json" in wf
    assert "periodic_integrity_sampling.json" in wf
    assert "security_events.jsonl" in wf
    assert "security_event_export.json" in wf
    assert "security_event_schema_gate.json" in wf
    assert "telemetry_completeness_sli_gate.json" in wf
    assert "telemetry_timeliness_sli_gate.json" in wf
    assert "telemetry_integrity_sli_gate.json" in wf
    assert "telemetry_integrity_trend_alert.json" in wf
    assert "security_pipeline_reliability_dashboard.json" in wf
    assert "security_pipeline_reliability_history.json" in wf
    assert "security_posture_executive_summary.json" in wf
    assert "formal_security_review_artifact.json" in wf
    assert "formal_security_review_artifact.json.sig" in wf
    assert "security_gate_test_coverage.json" in wf
    assert "hardening_todo_consistency_gate.json" in wf
    assert "security_trend_alert.json" in wf
    assert "key_provenance_continuity_gate.json" in wf
    assert "signature_algorithm_policy_gate.json" in wf
    assert "security_verification_summary.json" in wf
    assert "security_verification_summary.json.sig" in wf
    assert "security_gate_runtime_budget_gate.json" in wf
    assert "security_gate_runtime_history.json" in wf
    assert "semgrep --version" in wf
    assert 'python -c "import pkg_resources"' in wf
    assert "security-maintenance-artifacts" in wf
    assert "airgap-simulation-artifacts" in wf
    assert "offline_verify_bundle_export.json" in wf
    assert "offline_verification_gate.json" in wf
    assert "offline_verify_bundle/offline_verify_report.json" in wf
