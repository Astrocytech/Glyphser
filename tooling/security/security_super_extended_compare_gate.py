#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from tooling.lib.path_config import evidence_root

ROOT = Path(__file__).resolve().parents[2]
SUPER_REPORT = ROOT / "evidence" / "security" / "security_super_gate.json"
MANIFEST = ROOT / "tooling" / "security" / "security_super_gate_manifest.json"


def _script_from_cmd(cmd: list[Any]) -> str:
    if len(cmd) < 2:
        return ""
    part = cmd[1]
    return str(part) if isinstance(part, str) else ""


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    if not SUPER_REPORT.exists():
        findings.append("missing_super_gate_report")
    if not MANIFEST.exists():
        findings.append("missing_manifest")
    if findings:
        report = {
            "status": "FAIL",
            "findings": findings,
            "summary": {"core_failures": 0, "extended_failures": 0},
            "metadata": {"gate": "security_super_extended_compare_gate"},
        }
        out = evidence_root() / "security" / "security_super_extended_compare_gate.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"SECURITY_SUPER_EXTENDED_COMPARE_GATE: {report['status']}")
        print(f"Report: {out}")
        return 1

    payload = json.loads(SUPER_REPORT.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    core = set(manifest.get("core", []) if isinstance(manifest, dict) else [])
    extended = set(manifest.get("extended", []) if isinstance(manifest, dict) else [])
    results = payload.get("results", []) if isinstance(payload, dict) else []
    if not isinstance(results, list):
        results = []
    core_failures: list[str] = []
    extended_failures: list[str] = []
    unknown_failures: list[str] = []
    for rec in results:
        if not isinstance(rec, dict):
            continue
        if str(rec.get("status", "")) == "PASS":
            continue
        cmd = rec.get("cmd", [])
        if not isinstance(cmd, list):
            continue
        script = _script_from_cmd(cmd)
        if script in core:
            core_failures.append(script)
        elif script in extended:
            extended_failures.append(script)
        else:
            unknown_failures.append(script)
    for script in sorted(set(unknown_failures)):
        findings.append(f"unknown_failed_gate:{script}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "core_failures": len(set(core_failures)),
            "extended_failures": len(set(extended_failures)),
            "unknown_failures": len(set(unknown_failures)),
        },
        "metadata": {"gate": "security_super_extended_compare_gate"},
        "classification": {
            "core_failures": sorted(set(core_failures)),
            "extended_failures": sorted(set(extended_failures)),
            "unknown_failures": sorted(set(unknown_failures)),
        },
    }
    out = evidence_root() / "security" / "security_super_extended_compare_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"SECURITY_SUPER_EXTENDED_COMPARE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
