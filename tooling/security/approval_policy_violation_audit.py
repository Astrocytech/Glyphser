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


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _approval_violations(report: dict[str, Any]) -> list[str]:
    findings = report.get("findings", []) if isinstance(report, dict) else []
    if not isinstance(findings, list):
        return []
    markers = (
        "split_role_",
        "approval_",
        "missing_required_reviewer_group",
        "security_change_missing_ticket_or_adr",
        "missing_security_changelog_entry",
    )
    out: list[str] = []
    for item in findings:
        if not isinstance(item, str):
            continue
        if item.startswith(markers):
            out.append(item)
    return out


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    review_report = sec / "review_policy_gate.json"
    history_path = sec / "approval_policy_violation_audit_history.json"
    findings: list[str] = []

    current_violations: list[str] = []
    if review_report.exists():
        try:
            current_violations = sorted(set(_approval_violations(_load_json(review_report))))
        except Exception:
            findings.append("invalid_review_policy_gate_report")
    else:
        findings.append("missing_review_policy_gate_report")

    previous_open: list[str] = []
    if history_path.exists():
        try:
            history = _load_json(history_path)
            previous_raw = history.get("open_violations", []) if isinstance(history, dict) else []
            if isinstance(previous_raw, list):
                previous_open = sorted(set(str(x) for x in previous_raw if isinstance(x, str)))
        except Exception:
            findings.append("invalid_violation_audit_history")

    prev_set = set(previous_open)
    cur_set = set(current_violations)
    new_violations = sorted(cur_set - prev_set)
    recurring_violations = sorted(cur_set & prev_set)
    resolved_since_last = sorted(prev_set - cur_set)

    _write_json(
        history_path,
        {
            "open_violations": current_violations,
            "last_new_violations": new_violations,
            "last_resolved_violations": resolved_since_last,
        },
    )

    report = {
        "status": "WARN" if current_violations else "PASS",
        "findings": findings,
        "summary": {
            "current_open_violations": current_violations,
            "new_violations": new_violations,
            "recurring_violations": recurring_violations,
            "resolved_since_last": resolved_since_last,
        },
        "metadata": {"gate": "approval_policy_violation_audit"},
    }
    out = sec / "approval_policy_violation_audit.json"
    write_json_report(out, report)
    print(f"APPROVAL_POLICY_VIOLATION_AUDIT: {report['status']}")
    print(f"Report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
