#!/usr/bin/env python3
from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

REQUIRED_SNIPPETS = {
    ".github/workflows/ci.yml": [
        "security-matrix:",
        "security-events: write",
        "python tooling/security/install_security_toolchain.py",
        "if: github.event_name != 'pull_request' || github.event.pull_request.head.repo.fork == false",
        "python tooling/security/evidence_run_dir_guard.py --run-id",
        "python tooling/security/subprocess_allowlist_report.py",
        "python tooling/security/subprocess_direct_usage_gate.py",
        "python tooling/security/security_super_gate_manifest_gate.py",
        "python tooling/security/workflow_artifact_retention_gate.py",
        "python tooling/security/semgrep_rules_self_check_gate.py",
        "python tooling/security/workflow_policy_coverage_gate.py",
        "python tooling/security/workflow_risky_patterns_gate.py",
        "python tooling/security/workflow_deprecated_invocation_gate.py",
        "python tooling/security/policy_schema_validation_gate.py",
        "python tooling/security/security_schema_migration_tracker.py",
        "python tooling/security/security_evidence_corruption_gate.py",
        "python tooling/security/security_workflow_trigger_gate.py",
        "python tooling/security/security_critical_test_wiring_gate.py",
        "semgrep.json",
        "semgrep --version",
        'python -c "import pkg_resources"',
    ],
    ".github/workflows/security-maintenance.yml": [
        "security-maintenance:",
        "python tooling/security/install_security_toolchain.py",
        "python tooling/security/evidence_run_dir_guard.py --run-id",
        "python tooling/security/subprocess_allowlist_report.py",
        "python tooling/security/subprocess_direct_usage_gate.py",
        "python tooling/security/security_super_gate_manifest_gate.py",
        "python tooling/security/workflow_artifact_retention_gate.py",
        "python tooling/security/semgrep_rules_self_check_gate.py",
        "python tooling/security/workflow_policy_coverage_gate.py",
        "python tooling/security/workflow_risky_patterns_gate.py",
        "python tooling/security/workflow_deprecated_invocation_gate.py",
        "python tooling/security/policy_schema_validation_gate.py",
        "python tooling/security/security_schema_migration_tracker.py",
        "python tooling/security/security_evidence_corruption_gate.py",
        "python tooling/security/security_workflow_trigger_gate.py",
        "python tooling/security/security_critical_test_wiring_gate.py",
        "semgrep --version",
        'python -c "import pkg_resources"',
    ],
    ".github/workflows/security-super-extended.yml": [
        "security-super-extended:",
        "python tooling/security/install_security_toolchain.py",
        "python tooling/security/evidence_run_dir_guard.py --run-id",
        "semgrep --version",
        'python -c "import pkg_resources"',
    ],
}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    checked = 0
    for rel_path, snippets in REQUIRED_SNIPPETS.items():
        path = ROOT / rel_path
        if not path.exists():
            findings.append(f"missing_workflow_file:{rel_path}")
            continue
        checked += 1
        text = path.read_text(encoding="utf-8")
        for snippet in snippets:
            if snippet not in text:
                findings.append(f"missing_workflow_contract_snippet:{rel_path}:{snippet}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"checked_workflows": checked, "required_workflows": len(REQUIRED_SNIPPETS)},
        "metadata": {"gate": "security_workflow_contract_gate"},
    }
    out = evidence_root() / "security" / "security_workflow_contract_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_WORKFLOW_CONTRACT_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
