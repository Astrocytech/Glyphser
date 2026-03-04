#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from tooling.lib.path_config import evidence_root
from tooling.security.advanced_policy import load_policy
from tooling.security.report_io import write_json_report

ROOT = Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = load_policy()
    enforce = bool(policy.get("enforce_deployment_freeze", True))
    critical_reports = [str(x) for x in policy.get("critical_freeze_reports", []) if isinstance(x, str)]
    sec = evidence_root() / "security"
    findings: list[str] = []
    failing_reports: list[str] = []

    for name in critical_reports:
        path = sec / name
        if not path.exists():
            findings.append(f"missing_critical_report:{name}")
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            findings.append(f"invalid_critical_report_json:{name}")
            continue
        status = str(payload.get("status", "")).upper()
        if status == "FAIL":
            failing_reports.append(name)

    if enforce and failing_reports:
        findings.extend(f"critical_report_failed:{name}" for name in failing_reports)

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "enforce_deployment_freeze": enforce,
            "critical_reports_checked": critical_reports,
            "critical_reports_failed": failing_reports,
        },
        "metadata": {"gate": "deployment_freeze_gate"},
    }
    out = sec / "deployment_freeze_gate.json"
    write_json_report(out, report)
    print(f"DEPLOYMENT_FREEZE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
