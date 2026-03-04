from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_security_maintenance_workflow_wired() -> None:
    wf = (ROOT / ".github" / "workflows" / "security-maintenance.yml").read_text(encoding="utf-8")
    assert "schedule:" in wf
    assert "python tooling/security/dependency_refresh_report.py" in wf
    assert "python tooling/security/install_security_toolchain.py" in wf
    assert "GLYPHSER_EVIDENCE_ROOT: evidence/runs/${{ github.run_id }}/security-maintenance" in wf
    assert "python tooling/security/evidence_run_dir_guard.py --run-id" in wf
    assert "python tooling/security/policy_signature_gate.py --strict-key" in wf
    assert "python tooling/security/policy_schema_validation_gate.py" in wf
    assert "python tooling/security/security_schema_migration_tracker.py" in wf
    assert "python tooling/security/security_super_gate_manifest_gate.py" in wf
    assert "python tooling/security/security_evidence_corruption_gate.py" in wf
    assert "python tooling/security/security_toolchain_gate.py" in wf
    assert "python tooling/security/workflow_risky_patterns_gate.py" in wf
    assert "python tooling/security/workflow_deprecated_invocation_gate.py" in wf
    assert "python tooling/security/subprocess_allowlist_report.py" in wf
    assert "python tooling/security/subprocess_direct_usage_gate.py" in wf
    assert "python tooling/security/pip_audit_gate.py" in wf
    assert "python tooling/security/secret_scan_gate.py" in wf
    assert "python tooling/security/workflow_pinning_gate.py" in wf
    assert "python tooling/security/incident_response_gate.py" in wf
    assert "python tooling/security/org_secret_backend_gate.py" in wf
    assert "python tooling/security/secret_management_gate.py" in wf
    assert "python tooling/security/production_controls_gate.py" in wf
    assert "python tooling/security/third_party_pentest_gate.py --strict-key" in wf
    assert "python tooling/security/live_integrations_verify.py" in wf
    assert "GLYPHSER_WAF_HEALTH_URL" in wf
    assert "python tooling/security/live_rollout_gate.py --target live_integrations" in wf
    assert "python tooling/security/container_provenance_gate.py" in wf
    assert "python tooling/security/abuse_telemetry_snapshot.py" in wf
    assert "python tooling/security/abuse_telemetry_gate.py" in wf
    assert "python tooling/security/evidence_attestation_index.py --strict-key" in wf
    assert "python tooling/security/evidence_attestation_gate.py --strict-key" in wf
    assert "python tooling/security/provenance_signature_gate.py --strict-key" in wf
    assert "python tooling/security/slsa_attestation_gate.py" in wf
    assert "python tooling/security/workflow_evidence_scope_gate.py" in wf
    assert "python tooling/security/conformance_security_coupling_gate.py" in wf
    assert "python tooling/security/security_super_gate.py --strict-key" in wf
    assert "python tooling/security/security_workflow_trigger_gate.py" in wf
    assert "python tooling/security/security_critical_test_wiring_gate.py" in wf
    assert "security_workflow_contract_gate.json" in wf
    assert "workflow_risky_patterns_gate.json" in wf
    assert "workflow_deprecated_invocation_gate.json" in wf
    assert "subprocess_allowlist_report.json" in wf
    assert "subprocess_direct_usage_gate.json" in wf
    assert "policy_schema_validation_gate.json" in wf
    assert "security_schema_migration_tracker.json" in wf
    assert "security_super_gate_manifest_gate.json" in wf
    assert "security_evidence_corruption_gate.json" in wf
    assert "security_workflow_trigger_gate.json" in wf
    assert "security_critical_test_wiring_gate.json" in wf
    assert "security_sarif_permissions_gate.json" in wf
    assert "security_workflow_permissions_policy_gate.json" in wf
    assert "security_exception_suppression_gate.json" in wf
    assert "security_dead_gate_wiring_gate.json" in wf
    assert "security_gate_test_coverage.json" in wf
    assert "hardening_todo_consistency_gate.json" in wf
    assert "semgrep --version" in wf
    assert 'python -c "import pkg_resources"' in wf
    assert "security-maintenance-artifacts" in wf
