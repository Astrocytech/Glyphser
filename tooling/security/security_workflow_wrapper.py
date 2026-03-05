#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

run_checked = importlib.import_module("tooling.security.subprocess_policy").run_checked
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

WORKFLOW_REQUIREMENTS: dict[str, dict[str, list[str]]] = {
    "ci": {
        "env": ["GLYPHSER_EVIDENCE_ROOT", "TZ", "LC_ALL", "LANG"],
        "tools": ["semgrep", "pip-audit"],
    },
    "maintenance": {
        "env": ["GLYPHSER_EVIDENCE_ROOT", "TZ", "LC_ALL", "LANG"],
        "tools": ["semgrep", "pip-audit"],
    },
    "release": {
        "env": [
            "GLYPHSER_EVIDENCE_ROOT",
            "GLYPHSER_PROVENANCE_HMAC_KEY",
            "GLYPHSER_SECURITY_OWNER",
            "GLYPHSER_RELEASE_OWNER",
            "TZ",
            "LC_ALL",
            "LANG",
        ],
        "tools": ["semgrep", "pip-audit"],
    },
}


def _validate(workflow: str) -> tuple[list[str], dict[str, object]]:
    findings: list[str] = []
    req = WORKFLOW_REQUIREMENTS.get(workflow, {"env": [], "tools": []})
    env_names = req.get("env", [])
    tool_names = req.get("tools", [])
    if not isinstance(env_names, list):
        env_names = []
    if not isinstance(tool_names, list):
        tool_names = []

    missing_env: list[str] = []
    for name in env_names:
        if not isinstance(name, str):
            continue
        if not os.environ.get(name, "").strip():
            missing_env.append(name)
            findings.append(f"missing_env:{name}")

    missing_tools: list[str] = []
    for name in tool_names:
        if not isinstance(name, str):
            continue
        if shutil.which(name) is None:
            missing_tools.append(name)
            findings.append(f"missing_tool:{name}")

    summary = {
        "workflow": workflow,
        "required_env_count": len(env_names),
        "required_tool_count": len(tool_names),
        "missing_env": missing_env,
        "missing_tools": missing_tools,
    }
    return findings, summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pre-validate env/secrets/tools before running security workflow commands.")
    parser.add_argument("--workflow", required=True, choices=sorted(WORKFLOW_REQUIREMENTS.keys()))
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Optional command to run after validation.")
    args = parser.parse_args([] if argv is None else argv)

    findings, summary = _validate(args.workflow)
    command = args.command
    if command and command[0] == "--":
        command = command[1:]

    command_result = {
        "ran": False,
        "returncode": None,
        "stdout": "",
        "stderr": "",
    }

    status = "PASS" if not findings else "FAIL"
    if status == "PASS" and command:
        proc = run_checked(command, cwd=ROOT, timeout_sec=300.0, max_output_bytes=2_000_000)
        command_result = {
            "ran": True,
            "returncode": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
        }
        if proc.returncode != 0:
            status = "FAIL"
            findings.append(f"wrapped_command_failed:{proc.returncode}")

    report = {
        "status": status,
        "findings": findings,
        "summary": summary,
        "metadata": {
            "wrapper": "security_workflow_wrapper",
            "workflow": args.workflow,
            "command": command,
            "command_result": command_result,
        },
    }
    out = evidence_root() / "security" / f"security_workflow_wrapper_{args.workflow}.json"
    write_json_report(out, report)
    print(f"SECURITY_WORKFLOW_WRAPPER[{args.workflow}]: {status}")
    print(f"Report: {out}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
