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


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _str_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(v) for v in values]


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    findings: list[str] = []
    evaluated: list[str] = []

    waiver_report = _load(sec / "temporary_waiver_gate.json")
    reconciliation_report = _load(sec / "exception_waiver_reconciliation_gate.json")
    promotion_report = _load(sec / "promotion_policy_gate.json")

    if not waiver_report:
        findings.append("missing_required_report:temporary_waiver_gate")
    if not reconciliation_report:
        findings.append("missing_required_report:exception_waiver_reconciliation_gate")
    if not promotion_report:
        findings.append("missing_required_report:promotion_policy_gate")

    waiver_findings = _str_list(waiver_report.get("findings", []))
    expired_waiver_open = any(item.startswith("expired_waiver:") for item in waiver_findings)
    promotion_status = str(promotion_report.get("status", "MISSING")).upper()
    promotion_summary = promotion_report.get("summary", {})
    if not isinstance(promotion_summary, dict):
        promotion_summary = {}

    reconciliation_summary = reconciliation_report.get("summary", {})
    if not isinstance(reconciliation_summary, dict):
        reconciliation_summary = {}
    missing_closures = int(reconciliation_summary.get("missing_closures", 0) or 0)
    reconciliation_status = str(reconciliation_report.get("status", "MISSING")).upper()

    # Invariant ST-001: expired waivers must block promotion eligibility.
    evaluated.append("ST-001")
    if expired_waiver_open and promotion_status == "PASS":
        findings.append("invariant_violation:ST-001:expired_waiver_allows_promotion")

    # Invariant ST-002: unresolved waiver closures must block promotion eligibility.
    evaluated.append("ST-002")
    if missing_closures > 0 and promotion_status == "PASS":
        findings.append("invariant_violation:ST-002:missing_closure_allows_promotion")

    # Invariant ST-003: promotion eligibility requires exception closure gate PASS.
    evaluated.append("ST-003")
    if promotion_status == "PASS" and reconciliation_status != "PASS":
        findings.append("invariant_violation:ST-003:promotion_without_exception_closure_pass")

    # Invariant ST-004: override-based promotion must have validated override semantics.
    evaluated.append("ST-004")
    override_applied = bool(promotion_summary.get("override_applied", False))
    override_reason = str(promotion_summary.get("override_reason", "")).strip()
    soft_failures = promotion_summary.get("soft_failures", [])
    if not isinstance(soft_failures, list):
        soft_failures = []
    if override_applied and (override_reason != "override_valid" or not soft_failures):
        findings.append("invariant_violation:ST-004:invalid_override_transition")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "invariants_evaluated": evaluated,
            "expired_waiver_open": expired_waiver_open,
            "missing_closures": missing_closures,
            "reconciliation_status": reconciliation_status,
            "promotion_status": promotion_status,
        },
        "metadata": {"gate": "security_state_transition_invariants_gate"},
    }
    out = sec / "security_state_transition_invariants_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_STATE_TRANSITION_INVARIANTS_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
