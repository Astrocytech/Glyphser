#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

run_checked = importlib.import_module("tooling.security.subprocess_policy").run_checked
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
load_policy = importlib.import_module("tooling.security.advanced_policy").load_policy
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run periodic external audit simulation and emit closure artifact.")
    parser.add_argument("--audit-id", default="")
    args = parser.parse_args([] if argv is None else argv)

    audit_id = args.audit_id.strip() or f"AUDIT-SIM-{datetime.now(UTC).strftime('%Y%m%d')}"
    policy = load_policy()
    offline_bundle_dir = str(policy.get("offline_bundle_dir", "evidence/security/offline_verify_bundle"))
    steps = [
        (
            "export_offline_verify_bundle",
            [sys.executable, "tooling/security/export_offline_verify_bundle.py"],
            "evidence/security/offline_verify_bundle_export.json",
        ),
        (
            "offline_verify_bundle",
            [sys.executable, "tooling/security/offline_verify.py", "--bundle-dir", str(ROOT / offline_bundle_dir)],
            f"{offline_bundle_dir}/offline_verify_report.json",
        ),
        (
            "independent_verifier_profile",
            [sys.executable, "tooling/security/independent_verifier_profile_gate.py"],
            "evidence/security/independent_verifier_profile_gate.json",
        ),
        (
            "long_term_retention_manifest",
            [sys.executable, "tooling/security/long_term_retention_manifest.py"],
            "evidence/security/long_term_retention_manifest.json",
        ),
    ]

    results: list[dict[str, Any]] = []
    findings: list[str] = []
    closure_items: list[dict[str, Any]] = []
    for name, cmd, expected in steps:
        proc = run_checked(cmd, cwd=ROOT)
        ok = proc.returncode == 0
        if not ok:
            findings.append(f"simulation_step_failed:{name}:exit:{proc.returncode}")
        results.append(
            {
                "name": name,
                "command": cmd,
                "status": "PASS" if ok else "FAIL",
                "returncode": proc.returncode,
                "exit_reason": proc.exit_reason,
            }
        )
        closure_items.append(
            {
                "id": name,
                "verification_test": " ".join(cmd),
                "verified": ok,
                "evidence_path": expected,
            }
        )

    status = "PASS" if not findings else "FAIL"
    out_dir = evidence_root() / "security"
    report = {
        "status": status,
        "findings": findings,
        "summary": {"audit_id": audit_id, "steps": len(results), "passed": sum(1 for r in results if r["status"] == "PASS")},
        "metadata": {"gate": "external_audit_simulation", "network_access": "not_required"},
        "results": results,
    }
    closure = {
        "status": status,
        "incident_id": audit_id,
        "closure_type": "external_audit_simulation",
        "action_items": closure_items,
        "generated_at": datetime.now(UTC).isoformat(),
        "storage_location": str(policy.get("storage_location", "immutable://glyphser-security-evidence")),
    }
    report_path = out_dir / "external_audit_simulation.json"
    closure_path = out_dir / "external_audit_simulation_closure.json"
    write_json_report(report_path, report)
    write_json_report(closure_path, closure)
    print(f"EXTERNAL_AUDIT_SIMULATION: {status}")
    print(f"Report: {report_path}")
    print(f"Closure: {closure_path}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
