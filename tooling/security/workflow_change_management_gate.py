#!/usr/bin/env python3
from __future__ import annotations

import importlib
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

RATIONALE_FILE = "governance/security/workflow_change_rationale.md"


def _changed_files() -> list[str]:
    env_value = str(os.environ.get("GLYPHSER_CHANGED_FILES", "")).strip()
    if env_value:
        return [item.strip() for item in env_value.split(",") if item.strip()]
    try:
        proc = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except Exception:
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def main(argv: list[str] | None = None) -> int:
    _ = argv
    changed = _changed_files()
    findings: list[str] = []

    workflow_changes = sorted(p for p in changed if p.startswith(".github/workflows/") and "security" in p)
    policy_changes = sorted(p for p in changed if p.startswith("governance/security/") and p.endswith(".json"))
    rationale_changed = RATIONALE_FILE in changed
    rationale_env = str(os.environ.get("GLYPHSER_WORKFLOW_CHANGE_RATIONALE", "")).strip()

    if workflow_changes and not policy_changes and not rationale_changed and not rationale_env:
        findings.append("security_workflow_change_missing_policy_diff_or_rationale")
    for wf in workflow_changes:
        if not (policy_changes or rationale_changed or rationale_env):
            findings.append(f"unjustified_security_workflow_change:{wf}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "changed_files": len(changed),
            "security_workflow_changes": workflow_changes,
            "policy_changes": policy_changes,
            "rationale_changed": rationale_changed,
            "rationale_provided": bool(rationale_env),
        },
        "metadata": {"gate": "workflow_change_management_gate"},
    }
    out = evidence_root() / "security" / "workflow_change_management_gate.json"
    write_json_report(out, report)
    print(f"WORKFLOW_CHANGE_MANAGEMENT_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
