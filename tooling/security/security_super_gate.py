#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root


def _run(cmd: list[str]) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, check=False)
    return {
        "cmd": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "status": "PASS" if proc.returncode == 0 else "FAIL",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run consolidated security super gate.")
    parser.add_argument("--strict-key", action="store_true", help="Run signing-sensitive checks with strict key mode.")
    args = parser.parse_args([] if argv is None else argv)

    gates: list[list[str]] = [
        [sys.executable, "tooling/security/security_toolchain_gate.py"],
        [sys.executable, "tooling/security/key_management_gate.py"],
        [sys.executable, "tooling/security/governance_markdown_gate.py"],
        [sys.executable, "tooling/security/review_policy_gate.py"],
        [sys.executable, "tooling/security/file_permissions_gate.py"],
        [sys.executable, "tooling/security/policy_signature_gate.py", "--strict-key"] if args.strict_key else [sys.executable, "tooling/security/policy_signature_gate.py"],
        [sys.executable, "tooling/security/pip_audit_gate.py"],
        [sys.executable, "tooling/security/secret_scan_gate.py"],
        [sys.executable, "tooling/security/workflow_pinning_gate.py"],
        [sys.executable, "tooling/security/incident_response_gate.py"],
        [sys.executable, "tooling/security/org_secret_backend_gate.py"],
        [sys.executable, "tooling/security/secret_management_gate.py"],
        [sys.executable, "tooling/security/production_controls_gate.py"],
        [sys.executable, "tooling/security/abuse_telemetry_gate.py"],
        [sys.executable, "tooling/security/temporary_waiver_gate.py"],
        [sys.executable, "tooling/security/provenance_revocation_gate.py"],
        [sys.executable, "tooling/security/report_secret_leak_gate.py"],
        [sys.executable, "tooling/security/cosign_attestation_gate.py"],
        [sys.executable, "tooling/security/release_rollback_provenance_gate.py"],
        [sys.executable, "tooling/security/emergency_lockdown_gate.py"],
        [sys.executable, "tooling/security/evidence_chain_of_custody.py", "--strict-key"] if args.strict_key else [sys.executable, "tooling/security/evidence_chain_of_custody.py"],
        [sys.executable, "tooling/security/evidence_chain_of_custody.py", "--verify", "--strict-key"] if args.strict_key else [sys.executable, "tooling/security/evidence_chain_of_custody.py", "--verify"],
        [sys.executable, "tooling/security/conformance_security_coupling_gate.py"],
        [sys.executable, "tooling/security/security_slo_report.py"],
        [sys.executable, "tooling/security/security_trend_gate.py"],
        [sys.executable, "tooling/security/security_dashboard_export.py"],
        [sys.executable, "tooling/security/security_schema_normalization_gate.py"],
    ]

    results = [_run(cmd) for cmd in gates]
    failures = [r for r in results if r["status"] != "PASS"]
    report = {
        "status": "PASS" if not failures else "FAIL",
        "findings": ["gate_failed:" + " ".join(r["cmd"]) for r in failures],
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r["status"] == "PASS"),
            "failed": len(failures),
        },
        "metadata": {
            "runner": "security_super_gate",
            "strict_key": args.strict_key,
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
