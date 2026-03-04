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

DEPENDENT_REPORTS = [
    "workflow_risky_patterns_gate.json",
    "workflow_pinning.json",
    "security_workflow_permissions_policy_gate.json",
]


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    findings: list[str] = []
    checked = 0

    for name in DEPENDENT_REPORTS:
        checked += 1
        path = sec / name
        if not path.exists():
            findings.append(f"missing_dependency_report:{name}")
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            findings.append(f"invalid_dependency_report_json:{name}")
            continue
        status = str(payload.get("status", "")).upper()
        if status != "PASS":
            findings.append(f"dependency_report_not_pass:{name}:{status or 'UNKNOWN'}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"checked_dependency_reports": checked},
        "metadata": {"gate": "workflow_linter_gate"},
    }
    out = sec / "workflow_linter_gate.json"
    write_json_report(out, report)
    print(f"WORKFLOW_LINTER_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
