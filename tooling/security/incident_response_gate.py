#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
import importlib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _parse_utc(ts: str) -> datetime:
    parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return parsed.astimezone(UTC)


def _age_days(ts: str) -> int:
    delta = datetime.now(UTC) - _parse_utc(ts)
    return int(delta.total_seconds() // 86400)


def main() -> int:
    policy_path = ROOT / "governance" / "security" / "incident_response_policy.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    if not isinstance(policy, dict):
        raise ValueError("invalid incident response policy")

    findings: list[str] = []
    max_runbook_age = int(policy.get("max_runbook_age_days", 180))
    max_routing_age = int(policy.get("max_alert_routing_age_days", 30))
    max_rotation_age = int(policy.get("max_key_rotation_drill_age_days", 90))

    routing = policy.get("alert_routing_test", {})
    if not isinstance(routing, dict):
        findings.append("invalid alert_routing_test")
        routing = {}
    routing_ts = str(routing.get("last_tested_utc", ""))
    if not routing_ts:
        findings.append("missing alert_routing_test.last_tested_utc")
    else:
        if _age_days(routing_ts) > max_routing_age:
            findings.append("alert routing test stale")
    for key in ("primary_contact", "secondary_contact", "escalation_contact"):
        value = str(routing.get(key, "")).strip()
        if not value or "@" not in value:
            findings.append(f"invalid alert routing contact: {key}")

    rotation = policy.get("key_rotation_drill", {})
    if not isinstance(rotation, dict):
        findings.append("invalid key_rotation_drill")
        rotation = {}
    rotation_ts = str(rotation.get("last_drill_utc", ""))
    if not rotation_ts:
        findings.append("missing key_rotation_drill.last_drill_utc")
    else:
        if _age_days(rotation_ts) > max_rotation_age:
            findings.append("key rotation drill stale")
    rotation_evidence = str(rotation.get("evidence", "")).strip()
    if not rotation_evidence:
        findings.append("missing key rotation drill evidence path")
    else:
        path = ROOT / rotation_evidence
        if not path.exists():
            findings.append(f"missing key rotation drill evidence: {rotation_evidence}")

    runbooks = policy.get("runbooks", [])
    if not isinstance(runbooks, list):
        findings.append("invalid runbooks list")
        runbooks = []
    for idx, item in enumerate(runbooks):
        if not isinstance(item, dict):
            findings.append(f"invalid runbook entry #{idx}")
            continue
        rel = str(item.get("path", "")).strip()
        ts = str(item.get("last_reviewed_utc", "")).strip()
        if not rel:
            findings.append(f"missing runbook path #{idx}")
            continue
        runbook_path = ROOT / rel
        if not runbook_path.exists():
            findings.append(f"missing runbook file: {rel}")
        if not ts:
            findings.append(f"missing runbook review timestamp: {rel}")
        elif _age_days(ts) > max_runbook_age:
            findings.append(f"runbook stale: {rel}")

    payload: dict[str, Any] = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "max_runbook_age_days": max_runbook_age,
            "max_alert_routing_age_days": max_routing_age,
            "max_key_rotation_drill_age_days": max_rotation_age,
            "runbook_count": len(runbooks),
        },
        "metadata": {"gate": "incident_response_gate"},
        "policy": str(policy_path.relative_to(ROOT)).replace("\\", "/"),
    }
    out = evidence_root() / "security" / "incident_response.json"
    write_json_report(out, payload)
    print(f"INCIDENT_RESPONSE_GATE: {payload['status']}")
    print(f"Report: {out}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
