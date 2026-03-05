#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
run_checked = importlib.import_module("tooling.security.subprocess_policy").run_checked
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report
DEFAULT_TIMEOUT_SEC = 180.0
DEFAULT_MAX_OUTPUT_BYTES = 1_000_000


def _resource_budgets() -> tuple[float, int]:
    timeout = float(os.environ.get("GLYPHSER_PIP_AUDIT_TIMEOUT_SEC", str(DEFAULT_TIMEOUT_SEC)))
    max_output = int(os.environ.get("GLYPHSER_PIP_AUDIT_MAX_OUTPUT_BYTES", str(DEFAULT_MAX_OUTPUT_BYTES)))
    if timeout <= 0:
        raise ValueError("GLYPHSER_PIP_AUDIT_TIMEOUT_SEC must be > 0")
    if max_output <= 0:
        raise ValueError("GLYPHSER_PIP_AUDIT_MAX_OUTPUT_BYTES must be > 0")
    return timeout, max_output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run pip-audit and emit evidence report.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail the gate when pip-audit reports vulnerable dependencies.",
    )
    args = parser.parse_args([] if argv is None else argv)

    path_config = importlib.import_module("tooling.lib.path_config")
    out = path_config.evidence_root() / "security" / "pip_audit.json"
    cmd = [
        sys.executable,
        "-m",
        "pip_audit",
        "--format",
        "json",
        "--desc",
        "--skip-editable",
    ]
    timeout_sec, max_output_bytes = _resource_budgets()
    proc = run_checked(
        cmd,
        cwd=ROOT,
        timeout_sec=timeout_sec,
        max_output_bytes=max_output_bytes,
    )

    status = "PASS"
    findings: list[str] = []
    if proc.returncode == 1:
        status = "FAIL" if args.strict else "WARN"
        findings.append("vulnerabilities_reported")
    elif proc.returncode != 0:
        status = "FAIL"
        findings.append("pip_audit_execution_failed")

    payload: dict[str, object] = {
        "status": status,
        "returncode": proc.returncode,
        "command": cmd,
        "strict": args.strict,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "findings": findings,
        "summary": {
            "returncode": proc.returncode,
            "strict_mode": args.strict,
            "had_stdout": bool(proc.stdout.strip()),
            "resource_budget": {"timeout_sec": timeout_sec, "max_output_bytes": max_output_bytes},
        },
        "metadata": {"gate": "pip_audit_gate"},
    }
    if proc.stdout.strip():
        try:
            payload["report"] = json.loads(proc.stdout)
        except json.JSONDecodeError:
            payload["report_parse_error"] = "stdout was not valid JSON"

    write_json_report(out, payload)

    print(f"PIP_AUDIT_GATE: {payload['status']}")
    print(f"Report: {out}")
    return 0 if payload["status"] in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
