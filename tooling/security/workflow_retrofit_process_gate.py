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

POLICY = ROOT / "governance" / "security" / "workflow_retrofit_policy.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not POLICY.exists():
        findings.append("missing_workflow_retrofit_policy")
        policy: dict[str, Any] = {}
    else:
        try:
            policy = _load_json(POLICY)
        except Exception:
            policy = {}
            findings.append("invalid_workflow_retrofit_policy")

    workflows = policy.get("mandatory_workflows", []) if isinstance(policy, dict) else []
    controls = policy.get("required_controls", []) if isinstance(policy, dict) else []
    if not isinstance(workflows, list):
        workflows = []
        findings.append("invalid_mandatory_workflows")
    if not isinstance(controls, list):
        controls = []
        findings.append("invalid_required_controls")

    checked = 0
    for rel in workflows:
        if not isinstance(rel, str) or not rel.strip():
            findings.append("invalid_workflow_entry")
            continue
        path = ROOT / rel
        if not path.exists():
            findings.append(f"missing_mandatory_workflow:{rel}")
            continue
        text = path.read_text(encoding="utf-8")
        checked += 1
        for control in controls:
            if not isinstance(control, str) or not control.strip():
                findings.append("invalid_control_entry")
                continue
            if control not in text:
                findings.append(f"missing_retrofit_control:{rel}:{control}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "mandatory_workflows": len(workflows),
            "workflows_checked": checked,
            "required_controls": len(controls),
        },
        "metadata": {"gate": "workflow_retrofit_process_gate"},
    }
    out = evidence_root() / "security" / "workflow_retrofit_process_gate.json"
    write_json_report(out, report)
    print(f"WORKFLOW_RETROFIT_PROCESS_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
