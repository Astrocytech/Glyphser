#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

PROMOTION_REPORT = ROOT / "evidence" / "security" / "promotion_go_no_go_report.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    notes_rel = os.environ.get("GLYPHSER_RELEASE_NOTES_PATH", "CHANGELOG.md").strip() or "CHANGELOG.md"
    notes_path = ROOT / notes_rel

    decision = "UNKNOWN"
    if PROMOTION_REPORT.exists():
        payload = _load_json(PROMOTION_REPORT)
        summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
        if isinstance(summary, dict):
            decision = str(summary.get("decision", "UNKNOWN")).upper()
    else:
        findings.append("missing_promotion_go_no_go_report")

    if not notes_path.exists():
        findings.append(f"missing_release_notes:{notes_rel}")
        notes_text = ""
    else:
        notes_text = notes_path.read_text(encoding="utf-8")

    if notes_text:
        if "security control status summary" not in notes_text.lower():
            findings.append("missing_security_control_status_summary_section")
        if decision != "UNKNOWN" and decision not in notes_text.upper():
            findings.append(f"missing_promotion_decision_reference:{decision}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "release_notes_path": notes_rel,
            "promotion_decision": decision,
            "contains_security_summary": "missing_security_control_status_summary_section" not in findings,
        },
        "metadata": {"gate": "release_notes_security_status_gate"},
    }
    out = evidence_root() / "security" / "release_notes_security_status_gate.json"
    write_json_report(out, report)
    print(f"RELEASE_NOTES_SECURITY_STATUS_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
