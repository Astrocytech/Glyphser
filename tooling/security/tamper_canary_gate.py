#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from tooling.lib.path_config import evidence_root
from tooling.security.advanced_policy import load_policy

ROOT = Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = load_policy()
    expected = {x for x in policy.get("tamper_canary_reason_codes", []) if isinstance(x, str)}
    report_path = evidence_root() / "security" / "tamper_canary_report.json"
    findings: list[str] = []

    if not report_path.exists():
        findings.append("missing_tamper_canary_report")
        observed: set[str] = set()
    else:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
        observed = set(payload.get("reason_codes", [])) if isinstance(payload, dict) else set()

    for code in sorted(expected):
        if code not in observed:
            findings.append(f"missing_reason_code:{code}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"expected_reason_codes": sorted(expected), "observed_reason_codes": sorted(observed)},
        "metadata": {"gate": "tamper_canary_gate"},
    }
    out = evidence_root() / "security" / "tamper_canary_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"TAMPER_CANARY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
