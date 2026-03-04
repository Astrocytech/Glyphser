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
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report
PROFILE = ROOT / "governance" / "security" / "independent_verifier_profile.json"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    if not PROFILE.exists():
        findings.append("missing_independent_verifier_profile")
        payload: dict[str, object] = {}
    else:
        payload = json.loads(PROFILE.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            findings.append("invalid_independent_verifier_profile")
            payload = {}

    role = str(payload.get("role", "")).strip()
    if role != "read_only_verifier":
        findings.append("invalid_verifier_role")
    commands = payload.get("allowed_commands", [])
    if not isinstance(commands, list) or not commands:
        findings.append("missing_allowed_commands")
        commands = []
    forbidden_patterns = payload.get("forbidden_command_patterns", [])
    if not isinstance(forbidden_patterns, list):
        forbidden_patterns = []

    for cmd in commands:
        if not isinstance(cmd, str) or not cmd.strip():
            findings.append("invalid_allowed_command")
            continue
        lower = cmd.lower()
        for pattern in forbidden_patterns:
            if isinstance(pattern, str) and pattern.strip() and pattern.lower().strip() in lower:
                findings.append(f"forbidden_pattern_in_allowed_command:{cmd}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "profile_path": str(PROFILE.relative_to(ROOT)).replace("\\", "/"),
            "allowed_commands": len(commands),
        },
        "metadata": {"gate": "independent_verifier_profile_gate"},
    }
    out = evidence_root() / "security" / "independent_verifier_profile_gate.json"
    write_json_report(out, report)
    print(f"INDEPENDENT_VERIFIER_PROFILE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
