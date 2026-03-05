#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

PROFILE = ROOT / "governance" / "security" / "security_standards_profile.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not PROFILE.exists():
        findings.append("missing_security_standards_profile")
        payload: dict[str, Any] = {}
    else:
        try:
            payload = _load_json(PROFILE)
        except Exception:
            payload = {}
            findings.append("invalid_security_standards_profile")

    for field in ("profile_name", "owner", "reviewed_at_utc"):
        if not str(payload.get(field, "")).strip():
            findings.append(f"missing_field:{field}")

    consumer_repos = payload.get("consumer_repos", [])
    if not isinstance(consumer_repos, list) or not all(isinstance(item, str) and item.strip() for item in consumer_repos):
        findings.append("invalid_consumer_repos")
    required_controls = payload.get("required_controls", [])
    if not isinstance(required_controls, list) or not all(
        isinstance(item, str) and item.strip() for item in required_controls
    ):
        findings.append("invalid_required_controls")
    templates = payload.get("reference_templates", [])
    if not isinstance(templates, list) or not all(isinstance(item, str) and item.strip() for item in templates):
        findings.append("invalid_reference_templates")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "consumer_repos": len(consumer_repos) if isinstance(consumer_repos, list) else 0,
            "required_controls": len(required_controls) if isinstance(required_controls, list) else 0,
            "reference_templates": len(templates) if isinstance(templates, list) else 0,
        },
        "metadata": {"gate": "security_standards_profile_gate"},
    }
    out = evidence_root() / "security" / "security_standards_profile_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_STANDARDS_PROFILE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
