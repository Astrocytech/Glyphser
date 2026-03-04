#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
run_checked = importlib.import_module("tooling.security.subprocess_policy").run_checked
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


def _run(cmd: list[str]) -> dict[str, Any]:
    proc = run_checked(
        cmd,
        cwd=ROOT,
        timeout_sec=SUPER_GATE_SUBPROCESS_TIMEOUT_SEC,
        max_output_bytes=SUPER_GATE_SUBPROCESS_MAX_OUTPUT_BYTES,
    )
    return {
        "cmd": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "exit_reason": getattr(proc, "exit_reason", "exit"),
        "status": "PASS" if proc.returncode == 0 else "FAIL",
    }


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
    args = parser.parse_args([] if argv is None else argv)
    prereq_findings = _prereq_failures(strict_prereqs=args.strict_prereqs, strict_key=args.strict_key)

    gates: list[list[str]] = [
        [sys.executable, "tooling/security/security_toolchain_gate.py"],
        [sys.executable, "tooling/security/security_toolchain_lock_signature_gate.py"],
        [sys.executable, "tooling/security/security_scan_ordering_gate.py"],
        [sys.executable, "tooling/security/mypy_security_profile_gate.py"],
        [sys.executable, "tooling/security/ruff_security_profile_gate.py"],
        [sys.executable, "tooling/security/subprocess_allowlist_report.py"],
        [sys.executable, "tooling/security/subprocess_direct_usage_gate.py"],
        [sys.executable, "tooling/security/security_workflow_contract_gate.py"],
        [sys.executable, "tooling/security/security_super_gate_manifest_gate.py"],
        [sys.executable, "tooling/security/workflow_artifact_retention_gate.py"],
        [sys.executable, "tooling/security/semgrep_rules_self_check_gate.py"],
        [sys.executable, "tooling/security/workflow_policy_coverage_gate.py"],
        [sys.executable, "tooling/security/workflow_risky_patterns_gate.py"],
        [sys.executable, "tooling/security/workflow_deprecated_invocation_gate.py"],
        [sys.executable, "tooling/security/policy_schema_validation_gate.py"],
        [sys.executable, "tooling/security/security_schema_migration_tracker.py"],
        [sys.executable, "tooling/security/security_schema_strict_readiness_gate.py"],
        [sys.executable, "tooling/security/security_evidence_corruption_gate.py"],
        [sys.executable, "tooling/security/security_artifact_signature_coverage_gate.py"],
        [sys.executable, "tooling/security/security_unsigned_json_gate.py"],
        [sys.executable, "tooling/security/security_workflow_trigger_gate.py"],
        [sys.executable, "tooling/security/security_critical_test_wiring_gate.py"],
        [sys.executable, "tooling/security/security_sarif_permissions_gate.py"],
        [sys.executable, "tooling/security/security_workflow_permissions_policy_gate.py"],
        [sys.executable, "tooling/security/security_exception_suppression_gate.py"],
        [sys.executable, "tooling/security/security_dead_gate_wiring_gate.py"],
        [sys.executable, "tooling/security/hardening_todo_consistency_gate.py"],
        [sys.executable, "tooling/security/governance_markdown_gate.py"],
        [sys.executable, "tooling/security/review_policy_gate.py"],
        [sys.executable, "tooling/security/file_permissions_gate.py"],
        (
            [sys.executable, "tooling/security/policy_signature_gate.py", "--strict-key"]
            if args.strict_key
            else [sys.executable, "tooling/security/policy_signature_gate.py"]
        ),
        [sys.executable, "tooling/security/pip_audit_gate.py"],
        [sys.executable, "tooling/security/secret_scan_gate.py"],
        [sys.executable, "tooling/security/workflow_pinning_gate.py"],
        [sys.executable, "tooling/security/incident_response_gate.py"],
        [sys.executable, "tooling/security/org_secret_backend_gate.py"],
        [sys.executable, "tooling/security/secret_management_gate.py"],
        [sys.executable, "tooling/security/production_controls_gate.py"],
        [sys.executable, "tooling/security/runtime_api_state_schema_gate.py"],
        [sys.executable, "tooling/security/abuse_telemetry_gate.py"],
        [sys.executable, "tooling/security/temporary_waiver_gate.py"],
        [sys.executable, "tooling/security/provenance_revocation_gate.py"],
        [sys.executable, "tooling/security/report_secret_leak_gate.py"],
        [sys.executable, "tooling/security/security_gate_test_coverage_gate.py"],
        [sys.executable, "tooling/security/third_party_pentest_gate.py", "--strict-key"],
        [sys.executable, "tooling/security/live_integrations_verify.py", "--dry-run"],
        [sys.executable, "tooling/security/live_rollout_gate.py", "--allow-dry-run", "--allow-missing"],
        [sys.executable, "tooling/security/container_provenance_gate.py"],
        (
            [sys.executable, "tooling/security/evidence_attestation_index.py", "--strict-key"]
            if args.strict_key
            else [sys.executable, "tooling/security/evidence_attestation_index.py"]
        ),
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
        [sys.executable, "tooling/security/key_provenance_continuity_gate.py"],
        [sys.executable, "tooling/security/signature_algorithm_policy_gate.py"],
        (
            [sys.executable, "tooling/security/security_verification_summary.py", "--strict-key"]
            if args.strict_key
            else [sys.executable, "tooling/security/security_verification_summary.py"]
        ),
        [sys.executable, "tooling/security/slsa_attestation_gate.py"],
        [sys.executable, "tooling/security/workflow_evidence_scope_gate.py"],
        [sys.executable, "tooling/security/conformance_security_coupling_gate.py"],
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
        [sys.executable, "tooling/security/dependency_confusion_gate.py"],
        [sys.executable, "tooling/security/deterministic_env_gate.py"],
        [sys.executable, "tooling/security/archive_integrity_revalidation_gate.py"],
        [sys.executable, "tooling/security/compromised_runner_drill.py"],
    ]
    if args.include_extended:
        gates.extend(extended_gates)

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

    out = evidence_root() / "security" / "security_super_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"SECURITY_SUPER_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
