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

REQUIRED_EXPLICIT_PERMISSIONS = {
    "ci.yml",
    "security-maintenance.yml",
    "security-super-extended.yml",
    "release.yml",
}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    checked = 0
    security_workflows = 0
    wf_dir = ROOT / ".github" / "workflows"

    for wf in sorted(wf_dir.glob("*.yml")):
        text = wf.read_text(encoding="utf-8")
        checked += 1
        rel = str(wf.relative_to(ROOT)).replace("\\", "/")
        if "write-all" in text:
            findings.append(f"forbidden_permission_write_all:{rel}")
        if wf.name in REQUIRED_EXPLICIT_PERMISSIONS:
            security_workflows += 1
            if "permissions:" not in text:
                findings.append(f"missing_permissions_block:{rel}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"checked_workflows": checked, "security_workflows": security_workflows},
        "metadata": {"gate": "security_workflow_permissions_policy_gate"},
    }
    out = evidence_root() / "security" / "security_workflow_permissions_policy_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"SECURITY_WORKFLOW_PERMISSIONS_POLICY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
