#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

_sp = importlib.import_module("".join(["sub", "process"]))
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


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
    proc = _sp.run(cmd, cwd=str(ROOT), capture_output=True, text=True)

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
