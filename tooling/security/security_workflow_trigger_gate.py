#!/usr/bin/env python3
from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    ci_path = ROOT / ".github" / "workflows" / "ci.yml"
    ci = ci_path.read_text(encoding="utf-8")
    required_ci_snippets = [
        "on:",
        "push:",
        "pull_request:",
        "security-matrix:",
        'python-version: ["3.11", "3.12"]',
    ]
    for snippet in required_ci_snippets:
        if snippet not in ci:
            findings.append(f"missing_ci_trigger_or_job_snippet:{snippet}")

    extended_path = ROOT / ".github" / "workflows" / "security-super-extended.yml"
    if not extended_path.exists():
        findings.append("missing_workflow:security-super-extended.yml")
    else:
        ext = extended_path.read_text(encoding="utf-8")
        for snippet in ("schedule:", "workflow_dispatch:", "security-super-extended:"):
            if snippet not in ext:
                findings.append(f"missing_extended_trigger_or_job_snippet:{snippet}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"checked_workflows": 2},
        "metadata": {"gate": "security_workflow_trigger_gate"},
    }
    out = evidence_root() / "security" / "security_workflow_trigger_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_WORKFLOW_TRIGGER_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
