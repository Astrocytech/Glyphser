#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root
from tooling.security.report_io import write_json_report

POLICY = ROOT / "governance" / "security" / "security_artifact_signature_policy.json"


def _required_signed_json(payload: dict[str, Any]) -> tuple[list[str], list[str]]:
    findings: list[str] = []
    raw = payload.get("required_signed_security_json", [])
    if not isinstance(raw, list):
        return [], ["invalid_required_signed_security_json"]
    items: list[str] = []
    for item in raw:
        if not isinstance(item, str) or not item.strip():
            findings.append("invalid_required_signed_security_json_entry")
            continue
        value = item.strip()
        if not value.endswith(".json"):
            findings.append(f"required_signed_item_not_json:{value}")
            continue
        items.append(value)
    return sorted(set(items)), findings


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    if not isinstance(policy, dict):
        raise ValueError("invalid security artifact signature policy")
    required_json, policy_findings = _required_signed_json(policy)
    findings.extend(policy_findings)

    sec = evidence_root() / "security"
    checked = 0
    for name in required_json:
        checked += 1
        artifact = sec / name
        sig = sec / f"{name}.sig"
        if not artifact.exists():
            findings.append(f"required_artifact_missing:{name}")
            continue
        if not sig.exists():
            findings.append(f"required_artifact_signature_missing:{name}")
            continue
        if not sig.read_text(encoding="utf-8").strip():
            findings.append(f"required_artifact_signature_empty:{name}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"required_items": len(required_json), "checked_items": checked},
        "metadata": {"gate": "security_unsigned_json_gate"},
    }
    out = sec / "security_unsigned_json_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_UNSIGNED_JSON_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
