from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_ci_security_steps_are_wired() -> None:
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "security-matrix:" in ci
    assert 'python-version: ["3.11", "3.12"]' in ci
    assert "python tooling/security/install_security_toolchain.py" in ci
    assert "python tooling/security/security_cache_integrity_gate.py" in ci
    assert (
        "GLYPHSER_EVIDENCE_ROOT: evidence/runs/${{ github.run_id }}/security-matrix-${{ matrix.python-version }}" in ci
    )
    assert "python tooling/security/evidence_run_dir_guard.py --run-id" in ci
    assert "python tooling/security/policy_signature_gate.py --strict-key" in ci
    assert "python tooling/security/security_toolchain_gate.py" in ci
    assert "python tooling/security/toolchain_dependency_provenance_gate.py" in ci
    assert "python tooling/security/toolchain_source_failover_gate.py" in ci
    assert "python tooling/security/python_version_policy_gate.py" in ci
    assert "python tooling/security/subprocess_allowlist_report.py" in ci
    assert "python tooling/security/subprocess_direct_usage_gate.py" in ci
    assert "python tooling/security/security_workflow_contract_gate.py" in ci
    assert "python tooling/security/security_super_gate_manifest_gate.py" in ci
    assert "python tooling/security/workflow_artifact_retention_gate.py" in ci
    assert "python tooling/security/semgrep_rules_self_check_gate.py" in ci
    assert "python tooling/security/workflow_policy_coverage_gate.py" in ci
    assert "python tooling/security/scheduled_workflow_backpressure_gate.py" in ci
    assert "python tooling/security/workflow_risky_patterns_gate.py" in ci
    assert "python tooling/security/required_control_condition_bypass_gate.py" in ci
    assert "python tooling/security/workflow_change_management_gate.py" in ci
    assert "python tooling/security/workflow_deprecated_invocation_gate.py" in ci
    assert "python tooling/security/workflow_pin_change_approval_gate.py" in ci
    assert "python tooling/security/policy_schema_validation_gate.py" in ci
    assert "python tooling/security/security_schema_migration_tracker.py" in ci
    assert "python tooling/security/security_schema_strict_readiness_gate.py" in ci
    assert "python tooling/security/security_evidence_corruption_gate.py" in ci
    assert "python tooling/security/audit_archive_verify.py" in ci
    assert "python tooling/security/security_artifact_signature_coverage_gate.py" in ci
    assert "python tooling/security/artifact_path_case_conflict_gate.py" in ci
    assert "python tooling/security/security_unsigned_json_gate.py" in ci
    assert "python tooling/security/security_workflow_trigger_gate.py" in ci
    assert "python tooling/security/security_critical_test_wiring_gate.py" in ci
    assert "python tooling/security/security_sarif_permissions_gate.py" in ci
    assert "python tooling/security/security_workflow_permissions_policy_gate.py" in ci
    assert "python tooling/security/security_exception_suppression_gate.py" in ci
    assert "python tooling/security/security_dead_gate_wiring_gate.py" in ci
    assert "python tooling/security/hardening_todo_consistency_gate.py" in ci
    assert "python tooling/security/stale_policy_review_gate.py" in ci
    assert "python tooling/security/policy_deprecation_gate.py" in ci
    assert "python tooling/security/ownership_continuity_gate.py" in ci
    assert "python tooling/security/threat_control_mapping_gate.py" in ci
    assert "bandit -q -c tooling/security/bandit.yaml -r glyphser runtime tooling -l -ii" in ci
    assert "python tooling/security/pip_audit_gate.py" in ci
    assert "python tooling/security/dependency_freshness_gate.py" in ci
    assert "python tooling/security/dependency_registry_policy_gate.py" in ci
    assert "python tooling/security/lockfile_change_provenance_gate.py" in ci
    assert "python tooling/security/temp_directory_policy_gate.py" in ci
    assert "python tooling/security/secret_scan_gate.py" in ci
    assert "python tooling/security/workflow_pinning_gate.py" in ci
    assert "python tooling/security/external_action_owner_allowlist_gate.py" in ci
    assert "python tooling/security/third_party_action_sha_mapping_gate.py" in ci
    assert "python tooling/security/incident_response_gate.py" in ci
    assert "python tooling/security/post_incident_closure_gate.py" in ci
    assert "python tooling/security/org_secret_backend_gate.py" in ci
    assert "python tooling/security/secret_management_gate.py" in ci
    assert "python tooling/security/production_controls_gate.py" in ci
    assert "python tooling/security/third_party_pentest_gate.py --strict-key" in ci
    assert "python tooling/security/live_integrations_verify.py --dry-run" in ci
    assert "python tooling/security/live_rollout_gate.py --allow-dry-run --allow-missing" in ci
    assert "python tooling/security/container_provenance_gate.py" in ci
    assert "python tooling/security/container_registry_provenance_gate.py" in ci
    assert "python tooling/security/attestation_digest_match_gate.py" in ci
    assert "python tooling/security/abuse_telemetry_snapshot.py" in ci
    assert "python tooling/security/runtime_api_state_schema_gate.py" in ci
    assert "python tooling/security/runtime_api_input_surface_gate.py" in ci
    assert "python tooling/security/runtime_api_scope_matrix_gate.py" in ci
    assert "python tooling/security/fallback_secret_usage_gate.py" in ci
    assert "python tooling/security/abuse_telemetry_gate.py" in ci
    assert "python tooling/security/provenance_revocation_gate.py" in ci
    assert "python tooling/security/promotion_policy_gate.py" in ci
    assert "python tooling/security/security_state_transition_invariants_gate.py" in ci
    assert "python tooling/security/exception_waiver_reconciliation_gate.py" in ci
    assert "runtime_api_state_schema_gate.json" in ci
    assert "runtime_api_input_surface_gate.json" in ci
    assert "runtime_api_scope_matrix_gate.json" in ci
    assert "fallback_secret_usage_gate.json" in ci
    assert "provenance_revocation_gate.json" in ci
    assert "promotion_policy_gate.json" in ci
    assert "security_state_transition_invariants_gate.json" in ci
    assert "degraded_mode_evidence.json" in ci
    assert "workflow_pin_change_approval_gate.json" in ci
    assert "exception_waiver_reconciliation_gate.json" in ci
    assert "audit_archive_verify.json" in ci
    assert "security_artifact_signature_coverage_gate.json" in ci
    assert "artifact_path_case_conflict_gate.json" in ci
    assert "scheduled_workflow_backpressure_gate.json" in ci
    assert "required_control_condition_bypass_gate.json" in ci
    assert "workflow_change_management_gate.json" in ci
    assert "external_action_owner_allowlist_gate.json" in ci
    assert "third_party_action_sha_mapping_gate.json" in ci
    assert "security_unsigned_json_gate.json" in ci
    assert "dependency_freshness_gate.json" in ci
    assert "dependency_registry_policy_gate.json" in ci
    assert "lockfile_change_provenance_gate.json" in ci
    assert "temp_directory_policy_gate.json" in ci
    assert "stale_policy_review_gate.json" in ci
    assert "policy_deprecation_gate.json" in ci
    assert "ownership_continuity_gate.json" in ci
    assert "threat_control_mapping_gate.json" in ci
    assert "post_incident_closure_gate.json" in ci
    assert "container_registry_provenance_gate.json" in ci
    assert "attestation_digest_match_gate.json" in ci
    assert "python tooling/security/security_gate_test_coverage_gate.py" in ci
    assert "python tooling/security/evidence_attestation_index.py --strict-key" in ci
    assert "python tooling/security/evidence_attestation_gate.py --strict-key" in ci
    assert "python tooling/security/provenance_signature_gate.py --strict-key" in ci
    assert "python tooling/security/key_provenance_continuity_gate.py" in ci
    assert "python tooling/security/signature_algorithm_policy_gate.py" in ci
    assert "python tooling/security/security_verification_summary.py --strict-key" in ci
    assert "python tooling/security/security_event_export.py" in ci
    assert "python tooling/security/security_event_schema_gate.py" in ci
    assert "python tooling/security/slsa_attestation_gate.py" in ci
    assert "python tooling/security/workflow_evidence_scope_gate.py" in ci
    assert "python tooling/security/conformance_security_coupling_gate.py" in ci
    assert "python tooling/security/security_super_gate.py --strict-key" in ci
    assert "python tooling/security/security_gate_runtime_budget_gate.py" in ci
    assert "python tooling/security/security_pipeline_reliability_dashboard.py" in ci
    assert "python tooling/security/security_posture_executive_summary.py" in ci
    assert "python tooling/security/formal_security_review_artifact.py --strict-key" in ci
    assert "python tooling/security/security_artifacts.py" in ci
    assert "security_trend_alert.json" in ci
    assert "key_provenance_continuity_gate.json" in ci
    assert "signature_algorithm_policy_gate.json" in ci
    assert "security_verification_summary.json" in ci
    assert "security_verification_summary.json.sig" in ci
    assert "security_events.jsonl" in ci
    assert "security_event_export.json" in ci
    assert "security_event_schema_gate.json" in ci
    assert "ci_incident_replay_harness.json" in ci
    assert "security_gate_parity_snapshot.json" in ci
    assert "security_gate_runtime_budget_gate.json" in ci
    assert "security_gate_runtime_history.json" in ci
    assert "security_pipeline_reliability_dashboard.json" in ci
    assert "security_pipeline_reliability_history.json" in ci
    assert "security_posture_executive_summary.json" in ci
    assert "formal_security_review_artifact.json" in ci
    assert "formal_security_review_artifact.json.sig" in ci
    assert "python tooling/security/branch_protection_policy_gate.py" in ci
    assert "security_schema_strict_readiness_gate.json" in ci
    assert "python_version_policy_gate.json" in ci
    assert "security_toolchain_install_report.json" in ci
    assert "security_cache_integrity_gate.json" in ci
    assert "toolchain_dependency_provenance_gate.json" in ci
    assert "toolchain_source_failover_gate.json" in ci
    assert "toolchain_source_failover_history.json" in ci
    assert "bandit -q -c tooling/security/bandit.yaml -r glyphser runtime tooling -f json -o bandit.json -l -ii" in ci
    assert "python tooling/security/bandit_json_to_sarif.py --input bandit.json --output bandit.sarif" in ci
    assert "semgrep --config tooling/security/semgrep-rules.yml --error --sarif --output semgrep.sarif" in ci
    assert "semgrep --config tooling/security/semgrep-rules.yml --error --json --output semgrep.json" in ci
    assert "pytest -q tests/security" in ci
    assert "python tooling/security/ci_incident_replay_harness.py" in ci
    assert "python tooling/security/security_gate_parity_snapshot.py" in ci
    assert "python tooling/security/security_gate_parity_compare.py" in ci
    assert "--cov=tooling/security" in ci
    assert "python tooling/security/security_coverage_threshold_gate.py --coverage-file coverage.xml --min-pct 85" in ci
    assert "semgrep --version" in ci
    assert 'python -c "import pkg_resources"' in ci
    assert "name: security-artifacts-${{ matrix.python-version }}" in ci
    assert "security-gate-parity:" in ci
    assert "name: security-artifacts-3.11" in ci
    assert "name: security-artifacts-3.12" in ci
    assert "security-fs-permissions-parity:" in ci
    assert "os: [ubuntu-latest, macos-latest]" in ci
    assert "python tooling/security/file_permissions_gate.py" in ci
    assert "python tooling/security/file_permission_matrix_gate.py" in ci
    assert "name: security-fs-permissions-parity-${{ matrix.os }}" in ci
    assert "security-tooling-smoke-matrix:" in ci
    assert "GLYPHSER_EVIDENCE_ROOT: evidence/runs/${{ github.run_id }}/security-tooling-smoke-${{ matrix.os }}" in ci
    assert "python tooling/security/security_toolchain_gate.py" in ci
    assert "python tooling/security/semgrep_rules_self_check_gate.py" in ci
    assert "python tooling/security/runtime_api_scope_matrix_gate.py" in ci
    assert "python tooling/security/security_event_schema_gate.py" in ci
    assert "python tooling/security/security_super_gate.py --strict-prereqs" in ci
    assert "python tooling/security/signed_json_hash_equivalence_gate.py" in ci
    assert "python tooling/security/locale_variance_suite.py" in ci
    assert "python tooling/security/security_gate_parity_snapshot.py" in ci
    assert "name: security-tooling-smoke-${{ matrix.os }}" in ci
    assert "security_gate_parity_snapshot.json" in ci
    assert "security-signed-json-hash-equivalence:" in ci
    assert "name: security-tooling-smoke-ubuntu-latest" in ci
    assert "name: security-tooling-smoke-macos-latest" in ci
    assert "Compare signed JSON hash equivalence across OS" in ci
    assert "signed_json_hash_equivalence_gate.json" in ci
    assert "locale_variance_suite.json" in ci
    assert "uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683" in ci


def test_ci_conformance_step_is_wired() -> None:
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "run: python tooling/conformance/cli.py run" in ci
