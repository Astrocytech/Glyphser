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


def _age_days(ts: str) -> int:
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(UTC)
    return int((datetime.now(UTC) - dt).total_seconds() // 86400)


def main() -> int:
    policy_path = ROOT / "governance" / "security" / "production_controls_policy.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    if not isinstance(policy, dict):
        raise ValueError("invalid production controls policy")

    required = policy.get("required_controls", [])
    max_age = int(policy.get("max_snapshot_age_days", 30))
    snapshot_rel = str(policy.get("snapshot_path", "")).strip()
    if not isinstance(required, list) or not all(isinstance(x, str) and x for x in required):
        raise ValueError("required_controls must be list[str]")
    if not snapshot_rel:
        raise ValueError("missing snapshot_path")
    snapshot_path = ROOT / snapshot_rel
    findings: list[str] = []
    if not snapshot_path.exists():
        findings.append(f"missing snapshot: {snapshot_rel}")
        snap: dict[str, Any] = {}
    else:
        snap = json.loads(snapshot_path.read_text(encoding="utf-8"))
    updated = str(snap.get("updated_utc", "")).strip()
    if not updated:
        findings.append("missing snapshot updated_utc")
    elif _age_days(updated) > max_age:
        findings.append("production controls snapshot stale")
    controls = snap.get("controls", {})
    if not isinstance(controls, dict):
        controls = {}
    for ctl in required:
        obj = controls.get(ctl)
        if not isinstance(obj, dict):
            findings.append(f"missing control section: {ctl}")
            continue
        if obj.get("enabled") is not True:
            findings.append(f"control disabled: {ctl}")

    payload: dict[str, Any] = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "required_controls": len(required),
            "max_snapshot_age_days": max_age,
        },
        "metadata": {"gate": "production_controls_gate"},
    }
    out = evidence_root() / "security" / "production_controls.json"
    write_json_report(out, payload)
    print(f"PRODUCTION_CONTROLS_GATE: {payload['status']}")
    print(f"Report: {out}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
