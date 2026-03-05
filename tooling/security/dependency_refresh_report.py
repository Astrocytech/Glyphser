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
run_checked = importlib.import_module("tooling.security.subprocess_policy").run_checked
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def main() -> int:
    cmd = [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"]
    proc = run_checked(cmd, cwd=ROOT)
    payload: dict[str, object] = {
        "status": "PASS" if proc.returncode == 0 else "FAIL",
        "returncode": proc.returncode,
        "command": cmd,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }
    if proc.stdout.strip():
        try:
            payload["outdated"] = json.loads(proc.stdout)
        except json.JSONDecodeError:
            payload["parse_error"] = "stdout was not valid JSON"
    out = evidence_root() / "security" / "dependency_outdated.json"
    write_json_report(out, payload)
    print(f"DEPENDENCY_REFRESH_REPORT: {payload['status']}")
    print(f"Report: {out}")
    return 0 if proc.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
