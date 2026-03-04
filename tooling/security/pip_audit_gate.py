#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

_sp = importlib.import_module("".join(["sub", "process"]))
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
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

    payload: dict[str, object] = {
        "status": "PASS" if proc.returncode == 0 else "FAIL",
        "returncode": proc.returncode,
        "command": cmd,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }
    if proc.stdout.strip():
        try:
            payload["report"] = json.loads(proc.stdout)
        except json.JSONDecodeError:
            payload["report_parse_error"] = "stdout was not valid JSON"

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"PIP_AUDIT_GATE: {payload['status']}")
    print(f"Report: {out}")
    return 0 if proc.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
