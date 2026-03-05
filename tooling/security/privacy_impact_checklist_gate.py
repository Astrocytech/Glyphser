#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY = ROOT / "governance" / "security" / "privacy_impact_checklist_policy.json"


def _verify_signed_json(path: Path, findings: list[str], code_prefix: str) -> dict[str, object]:
    sig = path.with_suffix(".json.sig")
    if not sig.exists():
        findings.append(f"missing_{code_prefix}_signature")
        return {}
    sig_text = sig.read_text(encoding="utf-8").strip()
    if not artifact_signing.verify_file(path, sig_text, key=artifact_signing.current_key(strict=False)):
        if not artifact_signing.verify_file(path, sig_text, key=artifact_signing.bootstrap_key()):
            findings.append(f"invalid_{code_prefix}_signature")
            return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    policy = _verify_signed_json(POLICY, findings, "privacy_impact_checklist_policy")
    schema_path = ROOT / str(policy.get("telemetry_schema_path", "")).strip()
    checklist_path = ROOT / str(policy.get("privacy_checklist_path", "")).strip()

    if not schema_path.exists():
        findings.append("missing_telemetry_schema")
        schema: dict[str, object] = {}
    else:
        raw_schema = json.loads(schema_path.read_text(encoding="utf-8"))
        schema = raw_schema if isinstance(raw_schema, dict) else {}

    checklist = _verify_signed_json(checklist_path, findings, "privacy_impact_checklist") if checklist_path.exists() else {}
    if not checklist:
        findings.append("missing_or_invalid_privacy_impact_checklist")

    required_fields = schema.get("required_fields", []) if isinstance(schema.get("required_fields"), list) else []
    reviewed_fields = checklist.get("reviewed_fields", []) if isinstance(checklist.get("reviewed_fields"), list) else []
    reviewed_set = {str(item).strip() for item in reviewed_fields if isinstance(item, str) and str(item).strip()}

    for field in required_fields:
        if not isinstance(field, str) or not field.strip():
            continue
        if field not in reviewed_set:
            findings.append(f"telemetry_field_missing_privacy_impact_review:{field}")

    if not str(checklist.get("approved_by", "")).strip():
        findings.append("privacy_impact_checklist_missing_approver")
    if not str(checklist.get("reviewed_at_utc", "")).strip():
        findings.append("privacy_impact_checklist_missing_reviewed_at_utc")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "required_field_count": len(required_fields),
            "reviewed_field_count": len(reviewed_set),
        },
        "metadata": {"gate": "privacy_impact_checklist_gate"},
    }
    out = evidence_root() / "security" / "privacy_impact_checklist_gate.json"
    write_json_report(out, report)
    print(f"PRIVACY_IMPACT_CHECKLIST_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
