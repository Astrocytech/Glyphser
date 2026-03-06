#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
run_checked = importlib.import_module("tooling.security.subprocess_policy").run_checked
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report
SUPER_GATE_SUBPROCESS_TIMEOUT_SEC = 300.0
SUPER_GATE_SUBPROCESS_MAX_OUTPUT_BYTES = 2_000_000

REMEDIATION_HINTS = {
    "missing_tool:semgrep": "Install pinned security tools (`pip install semgrep==1.95.0 setuptools==75.8.0`).",
    "missing_tool:pip-audit": "Install pinned security tools (`pip install pip-audit==2.9.0`).",
    "missing_env:GLYPHSER_PROVENANCE_HMAC_KEY": "Export GLYPHSER_PROVENANCE_HMAC_KEY from repository or environment secrets.",
    "missing_env:TZ": "Set TZ=UTC for deterministic security gate outputs.",
    "missing_env:LC_ALL": "Set LC_ALL=C.UTF-8 for deterministic sorting/encoding behavior.",
    "missing_env:LANG": "Set LANG=C.UTF-8 for deterministic locale behavior.",
}

RULE_ID_SUPER_GATE_PASS = "SUPER_GATE_NO_FINDINGS"
RULE_ID_SUPER_GATE_FAIL = "SUPER_GATE_FINDINGS_PRESENT"
RULE_ID_SUBGATE_PASS = "SUBGATE_EXIT_ZERO"
RULE_ID_SUBGATE_FAIL = "SUBGATE_EXIT_NONZERO"
RULE_ID_PREREQ_MISSING_TOOL = "PREREQ_TOOL_MISSING"
RULE_ID_PREREQ_MISSING_ENV = "PREREQ_ENV_MISSING"
RULE_ID_UNKNOWN_SELECTED_GATE = "SELECTED_GATE_UNKNOWN"
RULE_ID_PREREQ_OTHER = "PREREQ_CONDITION_FAILED"


def _run(cmd: list[str]) -> dict[str, Any]:
    started = time.monotonic()
    proc = run_checked(
        cmd,
        cwd=ROOT,
        timeout_sec=SUPER_GATE_SUBPROCESS_TIMEOUT_SEC,
        max_output_bytes=SUPER_GATE_SUBPROCESS_MAX_OUTPUT_BYTES,
    )
    runtime_seconds = round(time.monotonic() - started, 6)
    return {
        "cmd": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "exit_reason": getattr(proc, "exit_reason", "exit"),
        "status": "PASS" if proc.returncode == 0 else "FAIL",
        "runtime_seconds": runtime_seconds,
    }


def _script_from_cmd(cmd: list[str]) -> str:
    if len(cmd) >= 2:
        return str(cmd[1])
    return str(cmd[0]) if cmd else ""


def _aggregation_digest(results: list[dict[str, Any]]) -> str:
    material: list[dict[str, Any]] = []
    for result in results:
        if not isinstance(result, dict):
            continue
        cmd = result.get("cmd", [])
        material.append(
            {
                "script": _script_from_cmd(cmd if isinstance(cmd, list) else []),
                "status": str(result.get("status", "")),
                "returncode": int(result.get("returncode", -1)),
                "exit_reason": str(result.get("exit_reason", "")),
            }
        )
    canonical = json.dumps(sorted(material, key=lambda item: item["script"]), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _prereq_failures(*, strict_prereqs: bool, strict_key: bool) -> list[str]:
    findings: list[str] = []
    if strict_prereqs and shutil.which("semgrep") is None:
        findings.append("missing_tool:semgrep")
    if strict_prereqs and shutil.which("pip-audit") is None:
        findings.append("missing_tool:pip-audit")
    if strict_key and not os.environ.get("GLYPHSER_PROVENANCE_HMAC_KEY", "").strip():
        findings.append("missing_env:GLYPHSER_PROVENANCE_HMAC_KEY")
    if strict_prereqs:
        for name in ("TZ", "LC_ALL", "LANG"):
            if not os.environ.get(name, "").strip():
                findings.append(f"missing_env:{name}")
    return findings


def _prereq_diagnostics(findings: list[str]) -> list[dict[str, str]]:
    diagnostics: list[dict[str, str]] = []
    for finding in findings:
        diagnostics.append(
            {
                "finding": finding,
                "remediation": REMEDIATION_HINTS.get(
                    finding, "See security super-gate prerequisites and workflow environment configuration."
                ),
            }
        )
    return diagnostics


def _prereq_rule_id(finding: str) -> str:
    if finding.startswith("missing_tool:"):
        return RULE_ID_PREREQ_MISSING_TOOL
    if finding.startswith("missing_env:"):
        return RULE_ID_PREREQ_MISSING_ENV
    if finding.startswith("unknown_selected_gate:"):
        return RULE_ID_UNKNOWN_SELECTED_GATE
    return RULE_ID_PREREQ_OTHER


def _build_explainability(*, results: list[dict[str, Any]], prereq_findings: list[str], findings: list[str]) -> dict[str, Any]:
    decisions: list[dict[str, Any]] = []
    trace: list[dict[str, Any]] = []

    decisions.append(
        {
            "decision_id": "security_super_gate_overall",
            "decision": "PASS" if not findings else "FAIL",
            "rule_id": RULE_ID_SUPER_GATE_PASS if not findings else RULE_ID_SUPER_GATE_FAIL,
            "why": "No gate or prerequisite findings." if not findings else "One or more gate/prerequisite findings detected.",
            "finding_count": len(findings),
        }
    )
    trace.append(
        {
            "step": 1,
            "subject": "security_super_gate_overall",
            "rule_id": RULE_ID_SUPER_GATE_PASS if not findings else RULE_ID_SUPER_GATE_FAIL,
            "decision": "PASS" if not findings else "FAIL",
        }
    )

    step = 2
    for result in results:
        cmd = result.get("cmd", [])
        script = _script_from_cmd(cmd if isinstance(cmd, list) else [])
        status = str(result.get("status", "FAIL")).upper()
        is_pass = status == "PASS"
        decisions.append(
            {
                "decision_id": f"subgate:{script}",
                "decision": "PASS" if is_pass else "FAIL",
                "rule_id": RULE_ID_SUBGATE_PASS if is_pass else RULE_ID_SUBGATE_FAIL,
                "why": "Sub-gate returned zero exit status." if is_pass else "Sub-gate returned non-zero exit status.",
                "script": script,
                "returncode": int(result.get("returncode", -1)),
                "exit_reason": str(result.get("exit_reason", "exit")),
            }
        )
        trace.append(
            {
                "step": step,
                "subject": f"subgate:{script}",
                "rule_id": RULE_ID_SUBGATE_PASS if is_pass else RULE_ID_SUBGATE_FAIL,
                "decision": "PASS" if is_pass else "FAIL",
                "returncode": int(result.get("returncode", -1)),
            }
        )
        step += 1

    for finding in prereq_findings:
        decisions.append(
            {
                "decision_id": f"prereq:{finding}",
                "decision": "FAIL",
                "rule_id": _prereq_rule_id(finding),
                "why": "Super-gate prerequisite not satisfied.",
                "finding": finding,
            }
        )
        trace.append(
            {
                "step": step,
                "subject": f"prereq:{finding}",
                "rule_id": _prereq_rule_id(finding),
                "decision": "FAIL",
            }
        )
        step += 1

    return {
        "schema_version": "glyphser-security-super-gate-explainability.v1",
        "critical_decisions": decisions,
        "rule_evaluation_trace": trace,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run consolidated security super gate.")
    parser.add_argument("--strict-key", action="store_true", help="Run signing-sensitive checks with strict key mode.")
    parser.add_argument(
        "--strict-prereqs",
        action="store_true",
        help="Fail early if required tools/env/evidence prerequisites are missing.",
    )
    parser.add_argument(
        "--include-extended",
        action="store_true",
        help="Also run extended hardening gates that are outside baseline CI sequencing.",
    )
    parser.add_argument(
        "--only-gate",
        action="append",
        default=[],
        help="Run only specified gate script path(s); pass multiple times for multiple gates.",
    )
    parser.add_argument(
        "--explainability",
        action="store_true",
        help="Emit deterministic rule-based explainability for critical PASS/FAIL decisions.",
    )
    args = parser.parse_args([] if argv is None else argv)
    prereq_findings = _prereq_failures(strict_prereqs=args.strict_prereqs, strict_key=args.strict_key)

    gates: list[list[str]] = [
        [sys.executable, "tooling/security/security_toolchain_gate.py"],
        [sys.executable, "tooling/security/security_toolchain_lock_signature_gate.py"],
        [sys.executable, "tooling/security/security_toolchain_reproducibility_gate.py"],
        [sys.executable, "tooling/security/security_scan_ordering_gate.py"],
        [sys.executable, "tooling/security/mypy_security_profile_gate.py"],
        [sys.executable, "tooling/security/ruff_security_profile_gate.py"],
        [sys.executable, "tooling/security/security_gate_onboarding_checklist_gate.py"],
        [sys.executable, "tooling/security/subprocess_allowlist_report.py"],
        [sys.executable, "tooling/security/subprocess_direct_usage_gate.py"],
        [sys.executable, "tooling/security/security_workflow_contract_gate.py"],
        [sys.executable, "tooling/security/security_super_gate_manifest_gate.py"],
        [sys.executable, "tooling/security/security_gate_dependency_graph_gate.py"],
        [sys.executable, "tooling/security/critical_control_backup_verifier_gate.py"],
        [sys.executable, "tooling/security/critical_control_redundancy_report.py"],
        [sys.executable, "tooling/security/security_super_gate_membership_guard_gate.py"],
        [sys.executable, "tooling/security/workflow_artifact_retention_gate.py"],
        [sys.executable, "tooling/security/semgrep_rules_self_check_gate.py"],
        [sys.executable, "tooling/security/workflow_policy_coverage_gate.py"],
        [sys.executable, "tooling/security/workflow_risky_patterns_gate.py"],
        [sys.executable, "tooling/security/workflow_deprecated_invocation_gate.py"],
        [sys.executable, "tooling/security/workflow_pin_change_approval_gate.py"],
        [sys.executable, "tooling/security/file_mode_change_gate.py"],
        [sys.executable, "tooling/security/network_endpoint_documentation_gate.py"],
        [sys.executable, "tooling/security/security_rule_baseline_gate.py"],
        [sys.executable, "tooling/security/security_fixture_integrity_gate.py"],
        [sys.executable, "tooling/security/oncall_triage_sla_drill_gate.py"],
        [sys.executable, "tooling/security/runbook_command_health_gate.py"],
        [sys.executable, "tooling/security/fork_pr_sarif_skip_simulation_gate.py"],
        [sys.executable, "tooling/security/sarif_upload_prerequisite_gate.py"],
        [sys.executable, "tooling/security/sarif_fallback_upload_gate.py"],
        [sys.executable, "tooling/security/workflow_upload_wildcard_gate.py"],
        [sys.executable, "tooling/security/policy_schema_validation_gate.py"],
        [sys.executable, "tooling/security/security_report_schema_contract_gate.py"],
        [sys.executable, "tooling/security/policy_semantic_validation_gate.py"],
        [sys.executable, "tooling/security/security_retention_policy_gate.py"],
        [sys.executable, "tooling/security/environment_profile_policy_gate.py"],
        [sys.executable, "tooling/security/security_schema_compatibility_policy_gate.py"],
        [sys.executable, "tooling/security/security_schema_migration_tracker.py"],
        [sys.executable, "tooling/security/security_schema_strict_readiness_gate.py"],
        [sys.executable, "tooling/security/security_evidence_corruption_gate.py"],
        [sys.executable, "tooling/security/unicode_confusable_detection_gate.py"],
        [sys.executable, "tooling/security/audit_archive_verify.py"],
        [sys.executable, "tooling/security/security_artifact_signature_coverage_gate.py"],
        [sys.executable, "tooling/security/security_unsigned_json_gate.py"],
        [sys.executable, "tooling/security/security_workflow_trigger_gate.py"],
        [sys.executable, "tooling/security/security_critical_test_wiring_gate.py"],
        [sys.executable, "tooling/security/security_sarif_permissions_gate.py"],
        [sys.executable, "tooling/security/security_workflow_permissions_policy_gate.py"],
        [sys.executable, "tooling/security/strict_lane_exit_propagation_gate.py"],
        [sys.executable, "tooling/security/policy_manifest_ordering_gate.py"],
        [sys.executable, "tooling/security/security_exception_suppression_gate.py"],
        [sys.executable, "tooling/security/unconditional_return_zero_gate.py"],
        [sys.executable, "tooling/security/helper_script_enforcement_gate.py"],
        [sys.executable, "tooling/security/security_dead_gate_wiring_gate.py"],
        [sys.executable, "tooling/security/periodic_dead_gate_detection.py"],
        [sys.executable, "tooling/security/hardening_todo_consistency_gate.py"],
        [sys.executable, "tooling/security/hardening_todo_stale_item_gate.py"],
        [sys.executable, "tooling/security/governance_markdown_gate.py"],
        [sys.executable, "tooling/security/security_standards_profile_gate.py"],
        [sys.executable, "tooling/security/shared_security_template_compatibility_gate.py"],
        [sys.executable, "tooling/security/external_artifact_trust_contract_gate.py"],
        [sys.executable, "tooling/security/gate_decommissioning_policy_gate.py"],
        [sys.executable, "tooling/security/workflow_retrofit_process_gate.py"],
        [sys.executable, "tooling/security/security_federation_manifest.py"],
        [sys.executable, "tooling/security/ecosystem_conformance_report.py"],
        [sys.executable, "tooling/security/security_posture_executive_summary.py"],
        [sys.executable, "tooling/security/control_posture_rag_export.py"],
        [sys.executable, "tooling/security/top_risk_unresolved_items_ranker.py"],
        [sys.executable, "tooling/security/incident_timeline_reconstruction.py"],
        [sys.executable, "tooling/security/annual_assurance_package_generator.py"],
        [sys.executable, "tooling/security/security_optimization_review_gate.py"],
        [sys.executable, "tooling/security/stale_policy_review_gate.py"],
        [sys.executable, "tooling/security/runbook_index_health_gate.py"],
        [sys.executable, "tooling/security/gate_runbook_coverage_gate.py"],
        [sys.executable, "tooling/security/threat_control_mapping_gate.py"],
        [sys.executable, "tooling/security/threat_model_change_attestation_gate.py"],
        [sys.executable, "tooling/security/review_policy_gate.py"],
        [sys.executable, "tooling/security/incident_regression_catalog_gate.py"],
        [sys.executable, "tooling/security/high_severity_incident_regression_gate.py"],
        [sys.executable, "tooling/security/file_permissions_gate.py"],
        [sys.executable, "tooling/security/fallback_secret_usage_gate.py"],
        (
            [sys.executable, "tooling/security/policy_signature_gate.py", "--strict-key"]
            if args.strict_key
            else [sys.executable, "tooling/security/policy_signature_gate.py"]
        ),
        [sys.executable, "tooling/security/pip_audit_gate.py"],
        [sys.executable, "tooling/security/bandit_baseline_gate.py"],
        [sys.executable, "tooling/security/secret_scan_gate.py"],
        [sys.executable, "tooling/security/workflow_pinning_gate.py"],
        [sys.executable, "tooling/security/workflow_linter_gate.py"],
        [sys.executable, "tooling/security/incident_response_gate.py"],
        [sys.executable, "tooling/security/containment_verification_gate.py"],
        [sys.executable, "tooling/security/post_incident_closure_gate.py"],
        [sys.executable, "tooling/security/org_secret_backend_gate.py"],
        [sys.executable, "tooling/security/secret_management_gate.py"],
        [sys.executable, "tooling/security/secret_origin_inventory_gate.py"],
        [sys.executable, "tooling/security/secret_rotation_metadata_gate.py"],
        [sys.executable, "tooling/security/stale_secret_usage_wiring_gate.py"],
        [sys.executable, "tooling/security/break_glass_secret_usage_gate.py"],
        [sys.executable, "tooling/security/offline_network_call_guard_gate.py"],
        [sys.executable, "tooling/security/production_controls_gate.py"],
        [sys.executable, "tooling/security/runtime_api_state_schema_gate.py"],
        [sys.executable, "tooling/security/runtime_api_input_surface_gate.py"],
        [sys.executable, "tooling/security/runtime_api_scope_matrix_gate.py"],
        [sys.executable, "tooling/security/abuse_telemetry_gate.py"],
        [sys.executable, "tooling/security/temporary_waiver_gate.py"],
        [sys.executable, "tooling/security/exception_waiver_reconciliation_gate.py"],
        [sys.executable, "tooling/security/exception_debt_gate.py"],
        [sys.executable, "tooling/security/provenance_revocation_gate.py"],
        [sys.executable, "tooling/security/promotion_policy_gate.py"],
        [sys.executable, "tooling/security/degraded_mode_evidence.py"],
        [sys.executable, "tooling/security/report_secret_leak_gate.py"],
        [sys.executable, "tooling/security/security_gate_test_coverage_gate.py"],
        [sys.executable, "tooling/security/stale_security_test_coverage_gate.py"],
        [sys.executable, "tooling/security/stale_security_fixture_gate.py"],
        [sys.executable, "tooling/security/third_party_pentest_gate.py", "--strict-key"],
        [sys.executable, "tooling/security/live_integrations_verify.py", "--dry-run"],
        [sys.executable, "tooling/security/live_rollout_gate.py", "--allow-dry-run", "--allow-missing"],
        [sys.executable, "tooling/security/container_provenance_gate.py"],
        [sys.executable, "tooling/security/container_registry_provenance_gate.py"],
        [sys.executable, "tooling/security/attestation_digest_match_gate.py"],
        (
            [sys.executable, "tooling/security/evidence_attestation_index.py", "--strict-key"]
            if args.strict_key
            else [sys.executable, "tooling/security/evidence_attestation_index.py"]
        ),
        [sys.executable, "tooling/security/attestation_index_signed_artifacts_gate.py"],
        (
            [sys.executable, "tooling/security/evidence_attestation_gate.py", "--strict-key"]
            if args.strict_key
            else [sys.executable, "tooling/security/evidence_attestation_gate.py"]
        ),
        (
            [sys.executable, "tooling/security/provenance_signature_gate.py", "--strict-key"]
            if args.strict_key
            else [sys.executable, "tooling/security/provenance_signature_gate.py"]
        ),
        (
            [sys.executable, "tooling/security/integrity_envelope_gate.py", "--strict-key"]
            if args.strict_key
            else [sys.executable, "tooling/security/integrity_envelope_gate.py"]
        ),
        [sys.executable, "tooling/security/key_provenance_continuity_gate.py"],
        [sys.executable, "tooling/security/signature_key_lineage_policy_gate.py"],
        [sys.executable, "tooling/security/key_rotation_cadence_gate.py"],
        [sys.executable, "tooling/security/envelope_signature_design_checklist_gate.py"],
        [sys.executable, "tooling/security/signature_algorithm_policy_gate.py"],
        [sys.executable, "tooling/security/crypto_parameter_review_gate.py"],
        (
        [sys.executable, "tooling/security/security_verification_summary.py", "--strict-key"]
            if args.strict_key
            else [sys.executable, "tooling/security/security_verification_summary.py"]
        ),
        [sys.executable, "tooling/security/security_cross_gate_consistency_gate.py"],
        [sys.executable, "tooling/security/security_actionable_findings_gate.py"],
        [sys.executable, "tooling/security/runner_integrity_fingerprint_gate.py"],
        [sys.executable, "tooling/security/workflow_env_injection_gate.py"],
        [sys.executable, "tooling/security/trusted_execution_context_gate.py"],
        [sys.executable, "tooling/security/untrusted_pr_secret_isolation_gate.py"],
        [sys.executable, "tooling/security/security_lineage_map_artifact.py"],
        [sys.executable, "tooling/security/security_lineage_consistency_gate.py"],
        [sys.executable, "tooling/security/security_event_export.py"],
        [sys.executable, "tooling/security/security_event_schema_gate.py"],
        [sys.executable, "tooling/security/telemetry_completeness_sli_gate.py"],
        [sys.executable, "tooling/security/telemetry_timeliness_sli_gate.py"],
        [sys.executable, "tooling/security/telemetry_integrity_sli_gate.py"],
        [sys.executable, "tooling/security/slsa_attestation_gate.py"],
        [sys.executable, "tooling/security/workflow_evidence_scope_gate.py"],
        [sys.executable, "tooling/security/conformance_security_coupling_gate.py"],
        [sys.executable, "tooling/security/deployment_freeze_gate.py"],
    ]

    extended_gates: list[list[str]] = [
        [sys.executable, "tooling/security/key_management_gate.py"],
        [sys.executable, "tooling/security/cosign_attestation_gate.py"],
        [sys.executable, "tooling/security/release_rollback_provenance_gate.py"],
        [sys.executable, "tooling/security/emergency_lockdown_gate.py"],
        (
            [sys.executable, "tooling/security/evidence_chain_of_custody.py", "--strict-key"]
            if args.strict_key
            else [sys.executable, "tooling/security/evidence_chain_of_custody.py"]
        ),
        (
            [sys.executable, "tooling/security/evidence_chain_of_custody.py", "--verify", "--strict-key"]
            if args.strict_key
            else [sys.executable, "tooling/security/evidence_chain_of_custody.py", "--verify"]
        ),
        [sys.executable, "tooling/security/security_slo_report.py"],
        [sys.executable, "tooling/security/security_trend_gate.py"],
        [sys.executable, "tooling/security/security_dashboard_export.py"],
        [sys.executable, "tooling/security/security_schema_normalization_gate.py"],
        [sys.executable, "tooling/security/security_baseline_gate.py"],
        [sys.executable, "tooling/security/crypto_agility_matrix_gate.py"],
        [sys.executable, "tooling/security/provenance_witness_quorum_gate.py"],
        [sys.executable, "tooling/security/transparency_log_export.py"],
        [sys.executable, "tooling/security/transparency_log_gate.py"],
        [sys.executable, "tooling/security/time_source_attestation_gate.py"],
        [sys.executable, "tooling/security/build_environment_drift_gate.py"],
        [sys.executable, "tooling/security/artifact_classification_gate.py"],
        [sys.executable, "tooling/security/deterministic_redaction_gate.py"],
        [sys.executable, "tooling/security/disaster_recovery_drill_gate.py"],
        [sys.executable, "tooling/security/key_compromise_dual_control_gate.py"],
        [sys.executable, "tooling/security/dependency_trust_gate.py"],
        [sys.executable, "tooling/security/security_workflow_evidence_bundle_gate.py"],
        [sys.executable, "tooling/security/upload_manifest_generate.py"],
        [sys.executable, "tooling/security/upload_manifest_completeness_gate.py"],
        [sys.executable, "tooling/security/replay_abuse_regression_gate.py"],
        [sys.executable, "tooling/security/exception_registry_gate.py"],
        [sys.executable, "tooling/security/lockdown_blast_radius_gate.py"],
        [sys.executable, "tooling/security/canonical_json_roundtrip_gate.py"],
        [sys.executable, "tooling/security/file_permission_matrix_gate.py"],
        [sys.executable, "tooling/security/tamper_canary_gate.py"],
        [sys.executable, "tooling/security/security_docs_traceability_gate.py"],
        [sys.executable, "tooling/security/sbom_diff_review_gate.py"],
        [sys.executable, "tooling/security/egress_policy_gate.py"],
        [sys.executable, "tooling/security/attestation_freshness_gate.py"],
        [sys.executable, "tooling/security/crypto_algorithm_policy_gate.py"],
        [sys.executable, "tooling/security/split_duty_gate.py"],
        [sys.executable, "tooling/security/export_offline_verify_bundle.py"],
        [sys.executable, "tooling/security/external_export_data_minimization_gate.py"],
        [sys.executable, "tooling/security/exported_security_evidence_api_contract_versioning_gate.py"],
        [sys.executable, "tooling/security/dependency_confusion_gate.py"],
        [sys.executable, "tooling/security/deterministic_env_gate.py"],
        [sys.executable, "tooling/security/archive_integrity_revalidation_gate.py"],
        [sys.executable, "tooling/security/compromised_runner_drill.py"],
        [sys.executable, "tooling/security/governance_compliance_delta_report.py"],
        [sys.executable, "tooling/security/governance_compliance_quarterly_snapshot.py"],
        [sys.executable, "tooling/security/gate_status_transition_anomaly_detector.py"],
        [sys.executable, "tooling/security/cross_run_suspicious_pattern_linkage_gate.py"],
        [sys.executable, "tooling/security/containment_auto_trigger_recommendations.py"],
        [sys.executable, "tooling/security/incident_severity_scoring_report.py"],
        [sys.executable, "tooling/security/evidence_notarization_checkpoint.py"],
        [sys.executable, "tooling/security/manifest_pointer_meta_chain.py"],
        [sys.executable, "tooling/security/archival_encryption_verification_gate.py"],
        [sys.executable, "tooling/security/quarterly_restore_simulation.py"],
        [sys.executable, "tooling/security/developer_mode_profile_gate.py"],
        [sys.executable, "tooling/security/promotion_go_no_go_report.py"],
        [sys.executable, "tooling/security/signed_promotion_decision_artifact.py"],
        [sys.executable, "tooling/security/release_notes_security_status_gate.py"],
        [sys.executable, "tooling/security/release_metadata_evidence_checksum.py"],
        [sys.executable, "tooling/security/lockfile_transitive_provenance_gate.py"],
        [sys.executable, "tooling/security/toolchain_binary_source_consistency_gate.py"],
        [sys.executable, "tooling/security/package_metadata_anomaly_gate.py"],
        [sys.executable, "tooling/security/mirrored_source_integrity_report.py"],
        [sys.executable, "tooling/security/chaos_security_scenario_report.py"],
        [sys.executable, "tooling/security/gate_retry_strategy_policy_gate.py"],
        [sys.executable, "tooling/security/branch_protection_policy_gate.py"],
        [sys.executable, "tooling/security/codeowners_security_coverage_gate.py"],
        [sys.executable, "tooling/security/permissions_audit_artifact.py"],
        [sys.executable, "tooling/security/emergency_access_review_gate.py"],
        [sys.executable, "tooling/security/independent_verifier_profile_gate.py"],
        [sys.executable, "tooling/security/offline_verification_gate.py"],
    ]
    if args.include_extended:
        gates.extend(extended_gates)

    selected = [str(item).strip() for item in args.only_gate if str(item).strip()]
    if selected:
        selected_set = set(selected)
        available = {_script_from_cmd(cmd) for cmd in gates}
        missing = sorted(selected_set - available)
        prereq_findings.extend(f"unknown_selected_gate:{name}" for name in missing)
        gates = [cmd for cmd in gates if _script_from_cmd(cmd) in selected_set]

    results = [_run(cmd) for cmd in gates]
    failures = [r for r in results if r["status"] != "PASS"]
    findings = ["gate_failed:" + " ".join(r["cmd"]) for r in failures] + prereq_findings
    prereq_diagnostics = _prereq_diagnostics(prereq_findings)
    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r["status"] == "PASS"),
            "failed": len(failures),
            "prereq_failures": len(prereq_findings),
            "partial_rerun": bool(selected),
            "selected_gate_count": len(gates) if selected else 0,
            "aggregation_digest": _aggregation_digest(results),
        },
        "metadata": {
            "runner": "security_super_gate",
            "strict_key": args.strict_key,
            "strict_prereqs": args.strict_prereqs,
            "subprocess_timeout_sec": SUPER_GATE_SUBPROCESS_TIMEOUT_SEC,
            "subprocess_max_output_bytes": SUPER_GATE_SUBPROCESS_MAX_OUTPUT_BYTES,
            "prereq_diagnostics": prereq_diagnostics,
        },
        "results": results,
    }
    if args.explainability:
        report["explainability"] = _build_explainability(results=results, prereq_findings=prereq_findings, findings=findings)

    out = evidence_root() / "security" / "security_super_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_SUPER_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
