#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY = ROOT / "governance" / "security" / "hardening_freeze_criteria_policy.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _as_upper_set(value: object) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {str(item).strip().upper() for item in value if str(item).strip()}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not POLICY.exists():
        findings.append("missing_hardening_freeze_criteria_policy")
        policy: dict[str, Any] = {}
    else:
        try:
            policy = _load_json(POLICY)
        except Exception:
            policy = {}
            findings.append("invalid_hardening_freeze_criteria_policy")

    allowed_triggers = _as_upper_set(policy.get("allowed_trigger_types", []))
    enforced_states = _as_upper_set(policy.get("enforced_states", ["OPEN", "IN_PROGRESS", "PENDING"]))
    registry_rel = str(policy.get("enforced_ticket_registry_path", "governance/security/hardening_ticket_registry.json")).strip()
    registry = ROOT / registry_rel

    if not allowed_triggers:
        findings.append("missing_allowed_trigger_types")

    if not registry.exists():
        findings.append("missing_hardening_ticket_registry")
        tickets: list[dict[str, Any]] = []
    else:
        payload = _load_json(registry)
        raw = payload.get("tickets", [])
        tickets = [item for item in raw if isinstance(item, dict)] if isinstance(raw, list) else []

    checked = 0
    for row in tickets:
        ticket_id = str(row.get("ticket_id", "")).strip().upper()
        state = str(row.get("state", "OPEN")).strip().upper()
        if not ticket_id or state not in enforced_states:
            continue
        checked += 1
        trigger_type = str(row.get("trigger_type", "")).strip().upper()
        trigger_ref = str(row.get("trigger_reference", "")).strip()
        verification_plan = str(row.get("verification_plan", "")).strip()
        duplicate_check_reference = str(row.get("duplicate_check_reference", "")).strip()
        duplicate_check_result = str(row.get("duplicate_check_result", "")).strip().lower()
        if not trigger_type:
            findings.append(f"missing_trigger_type:{ticket_id}")
            continue
        if trigger_type not in allowed_triggers:
            findings.append(f"disallowed_trigger_type:{ticket_id}:{trigger_type}")
        if not trigger_ref:
            findings.append(f"missing_trigger_reference:{ticket_id}")
        if not verification_plan:
            findings.append(f"missing_verification_plan:{ticket_id}")
        if not duplicate_check_reference:
            findings.append(f"missing_duplicate_check_reference:{ticket_id}")
        if duplicate_check_result != "no_duplicate_category":
            findings.append(f"speculative_or_duplicate_category_not_allowed:{ticket_id}:{duplicate_check_result or 'empty'}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "checked_tickets": checked,
            "allowed_trigger_types": sorted(allowed_triggers),
            "enforced_states": sorted(enforced_states),
            "ticket_registry": str(registry.relative_to(ROOT)).replace("\\", "/") if registry.exists() else registry_rel,
        },
        "metadata": {"gate": "hardening_freeze_criteria_gate"},
    }
    out = evidence_root() / "security" / "hardening_freeze_criteria_gate.json"
    write_json_report(out, report)
    print(f"HARDENING_FREEZE_CRITERIA_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
