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

CONTRACT = ROOT / "governance" / "security" / "security_report_schema_contract.json"
REQUIRED_FIELDS = {"status", "findings", "summary", "metadata", "schema_version"}
ALLOWED_STATUS_VALUES = {"PASS", "FAIL", "WARN"}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    payload: dict[str, object] = {}
    if not CONTRACT.exists():
        findings.append("missing_security_report_schema_contract")
    else:
        raw = json.loads(CONTRACT.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            findings.append("invalid_security_report_schema_contract")
        else:
            payload = raw

    required = payload.get("required_fields", [])
    if not isinstance(required, list) or {str(x) for x in required} != REQUIRED_FIELDS:
        findings.append("invalid_required_fields")

    values = payload.get("status_values", [])
    if not isinstance(values, list):
        findings.append("invalid_status_values")
    else:
        got = {str(x).upper() for x in values}
        if not ALLOWED_STATUS_VALUES.issubset(got):
            findings.append("missing_required_status_values")

    schema_version = payload.get("schema_version")
    if not isinstance(schema_version, int) or schema_version < 1:
        findings.append("invalid_schema_version")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "contract_path": str(CONTRACT.relative_to(ROOT)).replace("\\", "/"),
            "required_fields": sorted(REQUIRED_FIELDS),
        },
        "metadata": {"gate": "security_report_schema_contract_gate"},
    }
    out = evidence_root() / "security" / "security_report_schema_contract_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_REPORT_SCHEMA_CONTRACT_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
