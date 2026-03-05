#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root
from tooling.security.report_io import write_json_report

POLICY = ROOT / "governance" / "security" / "runner_integrity_fingerprint_policy.json"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    payload = json.loads(POLICY.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("runner fingerprint policy must be a JSON object")

    allowed_rows = payload.get("allowed_fingerprints", [])
    required_envs = {str(x).strip().lower() for x in payload.get("require_match_in_envs", []) if str(x).strip()}
    if not isinstance(allowed_rows, list):
        raise ValueError("allowed_fingerprints must be a list")

    env_hint = os.environ.get("GLYPHSER_ENV", "").strip().lower()
    runner_os = os.environ.get("RUNNER_OS", platform.system()).strip().lower()
    python_minor = f"{sys.version_info.major}.{sys.version_info.minor}"
    toolchain_id = os.environ.get("GLYPHSER_RUNNER_TOOLCHAIN_ID", "").strip()

    current = {"runner_os": runner_os, "python_minor": python_minor, "toolchain_id": toolchain_id}
    matches = 0
    for row in allowed_rows:
        if not isinstance(row, dict):
            continue
        row_os = str(row.get("runner_os", "")).strip().lower()
        row_py = str(row.get("python_minor", "")).strip()
        row_toolchain = str(row.get("toolchain_id", "")).strip()
        if row_os and row_os != runner_os:
            continue
        if row_py and row_py != python_minor:
            continue
        if row_toolchain and row_toolchain != toolchain_id:
            continue
        matches += 1

    if env_hint in required_envs and matches == 0:
        findings.append(f"runner_fingerprint_not_allowlisted:{runner_os}:{python_minor}:{toolchain_id or 'none'}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "environment": env_hint or "unspecified",
            "current_fingerprint": current,
            "allowlisted_match_count": matches,
            "policy_entries": len([row for row in allowed_rows if isinstance(row, dict)]),
        },
        "metadata": {"gate": "runner_integrity_fingerprint_gate"},
    }
    out = evidence_root() / "security" / "runner_integrity_fingerprint_gate.json"
    write_json_report(out, report)
    print(f"RUNNER_INTEGRITY_FINGERPRINT_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
