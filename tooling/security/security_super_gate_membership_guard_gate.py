#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from tooling.lib.path_config import evidence_root

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "tooling" / "security" / "security_super_gate_manifest.json"
BASELINE = ROOT / "governance" / "security" / "security_super_gate_membership_baseline.json"


def _as_list(payload: Any, key: str) -> list[str]:
    if not isinstance(payload, dict):
        return []
    raw = payload.get(key, [])
    if not isinstance(raw, list):
        return []
    out: list[str] = []
    for item in raw:
        if isinstance(item, str) and item.strip():
            out.append(item.strip())
    return out


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    if not MANIFEST.exists():
        findings.append("missing_manifest")
    if not BASELINE.exists():
        findings.append("missing_baseline")
    if findings:
        report = {
            "status": "FAIL",
            "findings": findings,
            "summary": {"required_core": 0, "required_extended": 0},
            "metadata": {"gate": "security_super_gate_membership_guard_gate"},
        }
        out = evidence_root() / "security" / "security_super_gate_membership_guard_gate.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"SECURITY_SUPER_GATE_MEMBERSHIP_GUARD_GATE: {report['status']}")
        print(f"Report: {out}")
        return 1

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    core = set(_as_list(manifest, "core"))
    extended = set(_as_list(manifest, "extended"))
    req_core = _as_list(baseline, "required_core")
    req_extended = _as_list(baseline, "required_extended")
    for entry in req_core:
        if entry not in core:
            findings.append(f"missing_required_core:{entry}")
    for entry in req_extended:
        if entry not in extended:
            findings.append(f"missing_required_extended:{entry}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "required_core": len(req_core),
            "required_extended": len(req_extended),
            "manifest_core": len(core),
            "manifest_extended": len(extended),
        },
        "metadata": {"gate": "security_super_gate_membership_guard_gate"},
    }
    out = evidence_root() / "security" / "security_super_gate_membership_guard_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"SECURITY_SUPER_GATE_MEMBERSHIP_GUARD_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
