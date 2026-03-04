#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
load_policy = importlib.import_module("tooling.security.advanced_policy").load_policy
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = load_policy()
    required = [x for x in policy.get("required_env_vars", []) if isinstance(x, str)]
    required_tz = str(policy.get("required_timezone", "UTC"))
    findings: list[str] = []
    enforce = (
        os.environ.get("CI", "").strip().lower() == "true"
        or os.environ.get("GLYPHSER_STRICT_ENV_GATE", "").strip() == "1"
    )
    observed: dict[str, str] = {}

    for name in required:
        value = os.environ.get(name, "")
        observed[name] = value
        if enforce and not value:
            findings.append(f"missing_env:{name}")
    tz_value = os.environ.get("TZ", "")
    if enforce and tz_value and tz_value != required_tz:
        findings.append(f"timezone_not_pinned:{tz_value}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"required": required, "observed": observed, "required_timezone": required_tz, "enforce": enforce},
        "metadata": {"gate": "deterministic_env_gate"},
    }
    out = evidence_root() / "security" / "deterministic_env_gate.json"
    write_json_report(out, report)
    print(f"DETERMINISTIC_ENV_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
