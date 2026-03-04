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

POLICY_PATH = ROOT / "governance" / "security" / "workflow_policy_coverage.json"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    if not POLICY_PATH.exists():
        findings.append("missing_policy:governance/security/workflow_policy_coverage.json")
        policy_workflows: set[str] = set()
    else:
        payload = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("invalid workflow policy coverage format")
        raw = payload.get("workflows", [])
        if not isinstance(raw, list) or not all(isinstance(x, str) for x in raw):
            raise ValueError("workflow coverage policy must contain list[str] under workflows")
        policy_workflows = set(raw)

    actual_workflows = {p.name for p in sorted((ROOT / ".github" / "workflows").glob("*.yml"))}
    for name in sorted(actual_workflows - policy_workflows):
        findings.append(f"workflow_not_covered_by_policy:{name}")
    for name in sorted(policy_workflows - actual_workflows):
        findings.append(f"policy_lists_missing_workflow:{name}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"actual_workflows": len(actual_workflows), "policy_workflows": len(policy_workflows)},
        "metadata": {"gate": "workflow_policy_coverage_gate"},
    }
    out = evidence_root() / "security" / "workflow_policy_coverage_gate.json"
    write_json_report(out, report)
    print(f"WORKFLOW_POLICY_COVERAGE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
