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

POLICY = ROOT / "governance" / "security" / "gate_retry_strategy_policy.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not POLICY.exists():
        findings.append("missing_gate_retry_strategy_policy")
        policy: dict[str, Any] = {}
    else:
        policy = _load_json(POLICY)

    max_attempts = int(policy.get("max_attempts", 0) or 0)
    allowed = {str(x).strip() for x in policy.get("allowed_retry_gates", []) if isinstance(x, str) and str(x).strip()}
    require_seed = bool(policy.get("require_deterministic_seed", True))
    events_rel = str(policy.get("retry_events_path", "evidence/security/gate_retry_events.json")).strip()
    events_path = ROOT / events_rel if events_rel else Path("")

    if max_attempts <= 0:
        findings.append("invalid_max_attempts")

    if events_rel and events_path.exists():
        payload = _load_json(events_path)
        events = payload.get("events", []) if isinstance(payload, dict) else []
        if not isinstance(events, list):
            events = []
            findings.append("invalid_retry_events_payload")
    else:
        events = []

    for idx, item in enumerate(events):
        if not isinstance(item, dict):
            findings.append(f"invalid_retry_event:{idx}")
            continue
        gate = str(item.get("gate", "")).strip()
        attempt = int(item.get("attempt", 0) or 0)
        seeded = bool(item.get("deterministic_seeded", False))
        if gate not in allowed:
            findings.append(f"retry_gate_not_allowed:{gate}")
        if attempt > max_attempts:
            findings.append(f"retry_attempt_exceeds_max:{gate}:{attempt}:{max_attempts}")
        if require_seed and not seeded:
            findings.append(f"retry_missing_deterministic_seed:{gate}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "max_attempts": max_attempts,
            "allowed_retry_gates": sorted(allowed),
            "retry_events_evaluated": len(events),
            "require_deterministic_seed": require_seed,
            "retry_events_path": events_rel,
        },
        "metadata": {"gate": "gate_retry_strategy_policy_gate"},
    }

    out = evidence_root() / "security" / "gate_retry_strategy_policy_gate.json"
    write_json_report(out, report)
    print(f"GATE_RETRY_STRATEGY_POLICY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
