#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from tooling.lib.path_config import evidence_root
from tooling.security.report_io import write_json_report

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "governance" / "security" / "environment_profile_policy.json"
BOOLEAN_KEYS = ["require_strict_key", "require_signed_attestations", "allow_policy_fallbacks"]


def main(argv: list[str] | None = None) -> int:
    _ = argv
    payload = json.loads(POLICY.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("invalid environment profile policy")
    profiles = payload.get("profiles", {})
    order = payload.get("inheritance_order", [])
    findings: list[str] = []
    if not isinstance(profiles, dict):
        profiles = {}
        findings.append("invalid_profiles")
    if not isinstance(order, list):
        order = []
        findings.append("invalid_inheritance_order")

    for name in order:
        if str(name) not in profiles:
            findings.append(f"missing_profile:{name}")

    # strict inheritance: as we move right, strict flags cannot weaken.
    previous: dict[str, bool] | None = None
    for name in order:
        profile = profiles.get(str(name), {})
        if not isinstance(profile, dict):
            findings.append(f"invalid_profile:{name}")
            continue
        current: dict[str, bool] = {}
        for key in BOOLEAN_KEYS:
            value = profile.get(key, None)
            if not isinstance(value, bool):
                findings.append(f"invalid_profile_flag:{name}:{key}")
                continue
            current[key] = value
        if previous is not None and current:
            if previous.get("require_strict_key", False) and not current.get("require_strict_key", False):
                findings.append(f"inheritance_weakening:{name}:require_strict_key")
            if previous.get("require_signed_attestations", False) and not current.get("require_signed_attestations", False):
                findings.append(f"inheritance_weakening:{name}:require_signed_attestations")
            if not previous.get("allow_policy_fallbacks", True) and current.get("allow_policy_fallbacks", True):
                findings.append(f"inheritance_weakening:{name}:allow_policy_fallbacks")
        previous = current or previous

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"profiles": sorted(str(x) for x in profiles.keys()), "inheritance_order": [str(x) for x in order]},
        "metadata": {"gate": "environment_profile_policy_gate"},
    }
    out = evidence_root() / "security" / "environment_profile_policy_gate.json"
    write_json_report(out, report)
    print(f"ENVIRONMENT_PROFILE_POLICY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
