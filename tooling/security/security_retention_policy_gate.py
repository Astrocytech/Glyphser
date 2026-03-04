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

POLICY = ROOT / "governance" / "security" / "security_retention_policy.json"
REQUIRED_KEYS = {"storage_location", "retention_class", "legal_hold_supported", "manifest_required"}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    payload: dict[str, object] = {}
    if not POLICY.exists():
        findings.append("missing_security_retention_policy")
    else:
        raw = json.loads(POLICY.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            findings.append("invalid_security_retention_policy")
        else:
            payload = raw

    missing = sorted(key for key in REQUIRED_KEYS if key not in payload)
    findings.extend(f"missing_policy_field:{key}" for key in missing)
    if payload:
        if str(payload.get("storage_location", "")).strip() == "":
            findings.append("invalid_storage_location")
        if str(payload.get("retention_class", "")).strip() == "":
            findings.append("invalid_retention_class")
        if not isinstance(payload.get("legal_hold_supported"), bool):
            findings.append("invalid_legal_hold_supported")
        if not isinstance(payload.get("manifest_required"), bool):
            findings.append("invalid_manifest_required")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "policy_path": str(POLICY.relative_to(ROOT)).replace("\\", "/"),
            "required_fields": sorted(REQUIRED_KEYS),
        },
        "metadata": {"gate": "security_retention_policy_gate"},
    }
    out = evidence_root() / "security" / "security_retention_policy_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_RETENTION_POLICY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
