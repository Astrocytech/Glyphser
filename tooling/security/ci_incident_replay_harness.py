#!/usr/bin/env python3
from __future__ import annotations

import argparse
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

DEFAULT_FIXTURE = ROOT / "artifacts" / "inputs" / "fixtures" / "security-incidents" / "ci_incident_replay.json"


def _classify(log_excerpt: str) -> str:
    text = str(log_excerpt).lower()
    if "no module named pip_audit" in text or "pip_audit_execution_failed" in text:
        return "pip_audit_execution_failed"
    if "security-events: write" in text or "resource not accessible by integration" in text:
        return "security_events_permission_missing"
    if "missing required signing key env" in text:
        return "missing_required_signing_key"
    if "operation disabled by emergency lockdown policy" in text:
        return "lockdown_policy_enforced"
    return "unknown"


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Replay prior CI incident log excerpts and assert fixed behavior.")
    parser.add_argument("--fixture", default=str(DEFAULT_FIXTURE), help="Path to incident replay fixture JSON.")
    args = parser.parse_args([] if argv is None else argv)

    fixture = Path(args.fixture)
    data = _load(fixture)
    incidents = data.get("incidents", [])
    if not isinstance(incidents, list):
        incidents = []

    findings: list[str] = []
    checks: list[dict[str, str | bool]] = []
    for item in incidents:
        if not isinstance(item, dict):
            findings.append("invalid_incident_entry")
            continue
        ident = str(item.get("id", "")).strip() or "unknown"
        log_excerpt = str(item.get("log_excerpt", ""))
        expected = str(item.get("expected_reason", "")).strip()
        detected = _classify(log_excerpt)
        ok = bool(expected) and detected == expected
        checks.append({"id": ident, "expected": expected, "detected": detected, "ok": ok})
        if not ok:
            findings.append(f"incident_mismatch:{ident}:expected:{expected}:detected:{detected}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"checked_incidents": len(checks), "failed_incidents": len(findings), "fixture": str(fixture)},
        "metadata": {"gate": "ci_incident_replay_harness"},
        "checks": checks,
    }
    out = evidence_root() / "security" / "ci_incident_replay_harness.json"
    write_json_report(out, report)
    print(f"CI_INCIDENT_REPLAY_HARNESS: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
