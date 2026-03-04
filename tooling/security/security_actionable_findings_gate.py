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


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    findings: list[str] = []
    checked = 0

    for path in sorted(sec.glob("*.json")):
        if path.name == "security_actionable_findings_gate.json":
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(payload, dict):
            continue
        status = str(payload.get("status", "")).upper()
        if status != "FAIL":
            continue
        checked += 1
        report_findings = payload.get("findings", [])
        if not isinstance(report_findings, list) or not report_findings:
            findings.append(f"missing_fail_findings:{path.name}")
            continue
        for idx, item in enumerate(report_findings):
            s = str(item).strip()
            if not s or ":" not in s:
                findings.append(f"non_actionable_finding:{path.name}:{idx}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"checked_failed_reports": checked},
        "metadata": {"gate": "security_actionable_findings_gate"},
    }
    out = sec / "security_actionable_findings_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_ACTIONABLE_FINDINGS_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
