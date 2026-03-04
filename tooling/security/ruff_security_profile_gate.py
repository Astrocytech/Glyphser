#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import tomllib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

PROFILE = ROOT / "tooling" / "security" / "ruff_security_profile.toml"
REQUIRED_SELECT = {"E", "F", "I", "C90"}
MAX_COMPLEXITY_LIMIT = 12


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not PROFILE.exists():
        findings.append("missing_profile:tooling/security/ruff_security_profile.toml")
        profile: dict[str, object] = {}
    else:
        profile = tomllib.loads(PROFILE.read_text(encoding="utf-8"))

    lint = profile.get("lint", {}) if isinstance(profile, dict) else {}
    if not isinstance(lint, dict):
        lint = {}
    select = lint.get("select", [])
    if not isinstance(select, list):
        select = []
    selected = {str(x) for x in select}
    for rule in sorted(REQUIRED_SELECT):
        if rule not in selected:
            findings.append(f"missing_rule_select:{rule}")

    mccabe = lint.get("mccabe", {})
    if not isinstance(mccabe, dict):
        mccabe = {}
    max_complexity = mccabe.get("max-complexity", None)
    if not isinstance(max_complexity, int):
        findings.append("missing_mccabe_max_complexity")
    elif max_complexity > MAX_COMPLEXITY_LIMIT:
        findings.append(f"mccabe_max_too_high:{max_complexity}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "profile": str(PROFILE.relative_to(ROOT)).replace("\\", "/"),
            "required_rules": sorted(REQUIRED_SELECT),
            "max_complexity_limit": MAX_COMPLEXITY_LIMIT,
        },
        "metadata": {"gate": "ruff_security_profile_gate"},
    }
    out = evidence_root() / "security" / "ruff_security_profile_gate.json"
    write_json_report(out, report)
    print(f"RUFF_SECURITY_PROFILE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
