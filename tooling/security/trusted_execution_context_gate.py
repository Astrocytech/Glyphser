#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root
from tooling.security.report_io import write_json_report

POLICY = ROOT / "governance" / "security" / "trusted_execution_context_policy.json"
WORKFLOWS = ROOT / ".github" / "workflows"
RUNS_ON_RE = re.compile(r"^\s*runs-on:\s*(.+?)\s*$")


def _runs_on_values(text: str) -> list[str]:
    values: list[str] = []
    for line in text.splitlines():
        match = RUNS_ON_RE.match(line)
        if match:
            values.append(match.group(1).strip().strip('"').strip("'"))
    return values


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    payload = json.loads(POLICY.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("trusted execution context policy must be a JSON object")

    wf_types = payload.get("workflow_types", {})
    if not isinstance(wf_types, dict):
        raise ValueError("workflow_types must be an object")

    checked_workflows = 0
    for wf_type, cfg in wf_types.items():
        if not isinstance(cfg, dict):
            findings.append(f"invalid_workflow_type_config:{wf_type}")
            continue
        workflows = [str(x).strip() for x in cfg.get("workflows", []) if str(x).strip()]
        allowed_runs_on = {str(x).strip() for x in cfg.get("allowed_runs_on", []) if str(x).strip()}
        required_env = cfg.get("required_env", {})
        if not isinstance(required_env, dict):
            findings.append(f"invalid_required_env:{wf_type}")
            required_env = {}
        for wf_name in workflows:
            path = WORKFLOWS / wf_name
            checked_workflows += 1
            if not path.exists():
                findings.append(f"missing_workflow:{wf_type}:{wf_name}")
                continue
            text = path.read_text(encoding="utf-8")
            for runs_on in _runs_on_values(text):
                if allowed_runs_on and runs_on not in allowed_runs_on:
                    findings.append(f"disallowed_runs_on:{wf_type}:{wf_name}:{runs_on}")
            for key, expected_value in required_env.items():
                probe = f"{key}:"
                if probe not in text:
                    findings.append(f"missing_required_env:{wf_type}:{wf_name}:{key}")
                    continue
                if str(expected_value).strip() and f"{key}: \"{expected_value}\"" not in text and f"{key}: {expected_value}" not in text:
                    findings.append(f"required_env_value_mismatch:{wf_type}:{wf_name}:{key}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"workflow_types": len(wf_types), "workflows_checked": checked_workflows},
        "metadata": {"gate": "trusted_execution_context_gate"},
    }
    out = evidence_root() / "security" / "trusted_execution_context_gate.json"
    write_json_report(out, report)
    print(f"TRUSTED_EXECUTION_CONTEXT_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
