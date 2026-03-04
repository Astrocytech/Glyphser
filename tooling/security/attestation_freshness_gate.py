#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from tooling.lib.path_config import evidence_root
from tooling.security.advanced_policy import load_policy

ROOT = Path(__file__).resolve().parents[2]



def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = load_policy()
    max_age = int(policy.get("max_attestation_age_hours", 168))
    required = [x for x in policy.get("required_attestation_files", []) if isinstance(x, str)]
    now = datetime.now(UTC)
    findings: list[str] = []
    ages: dict[str, int] = {}

    for rel in required:
        path = ROOT / rel
        if not path.exists():
            findings.append(f"missing_attestation:{rel}")
            continue
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
        age_hours = int((now - mtime).total_seconds() // 3600)
        ages[rel] = age_hours
        if age_hours > max_age:
            findings.append(f"stale_attestation:{rel}:{age_hours}h")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"max_age_hours": max_age, "attestation_age_hours": ages},
        "metadata": {"gate": "attestation_freshness_gate"},
    }
    out = evidence_root() / "security" / "attestation_freshness_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"ATTESTATION_FRESHNESS_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
