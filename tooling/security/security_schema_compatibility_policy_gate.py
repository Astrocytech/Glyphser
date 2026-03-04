#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY = ROOT / "governance" / "security" / "security_schema_compatibility_policy.json"
MIN_MAJOR_EVIDENCE = {"adr_reference", "migration_plan", "approval_record"}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    payload = json.loads(POLICY.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("invalid schema compatibility policy")

    current = payload.get("current_schema_version")
    if not isinstance(current, int) or current < 1:
        findings.append("invalid_current_schema_version")
    if payload.get("minor_change_policy") != "additive_only":
        findings.append("invalid_minor_change_policy")
    if payload.get("major_change_policy") != "requires_migration_plan_and_approval":
        findings.append("invalid_major_change_policy")
    if payload.get("allow_optional_field_additions") is not True:
        findings.append("optional_field_additions_must_be_true")
    if payload.get("allow_required_field_removals") is not False:
        findings.append("required_field_removals_must_be_false")
    if payload.get("allow_field_type_changes_without_major") is not False:
        findings.append("field_type_change_without_major_must_be_false")

    required = payload.get("required_major_change_evidence", [])
    if not isinstance(required, list):
        findings.append("invalid_required_major_change_evidence")
        required_set: set[str] = set()
    else:
        required_set = {str(item) for item in required}
    missing = sorted(MIN_MAJOR_EVIDENCE - required_set)
    for item in missing:
        findings.append(f"missing_major_change_evidence:{item}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "policy": str(POLICY.relative_to(ROOT)).replace("\\", "/"),
            "required_major_change_evidence": sorted(MIN_MAJOR_EVIDENCE),
        },
        "metadata": {"gate": "security_schema_compatibility_policy_gate"},
    }
    out = evidence_root() / "security" / "security_schema_compatibility_policy_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_SCHEMA_COMPATIBILITY_POLICY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
