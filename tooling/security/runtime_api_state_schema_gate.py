#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root
from tooling.security.report_io import write_json_report

_REQUIRED_QUOTA_KEYS = [
    "token_requests",
    "token_submits",
    "job_reads",
    "job_replays",
    "job_last_replay_ts",
    "token_request_window",
    "auth_failures_by_token",
    "auth_failure_cooldown_until",
    "replay_window_by_token",
    "replay_window_by_job",
    "replay_window_job_tokens",
]


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    policy_path = ROOT / "governance" / "security" / "abuse_telemetry_policy.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    if not isinstance(policy, dict):
        raise ValueError("invalid abuse telemetry policy")

    configured_path = str(policy.get("runtime_api_state_path", "")).strip()
    if not configured_path:
        findings.append("missing_runtime_api_state_path")
        configured_path = "artifacts/generated/tmp/security/runtime_api_state.json"
    state_path = ROOT / configured_path

    required_counters = policy.get("required_runtime_counters", [])
    if not isinstance(required_counters, list) or not all(isinstance(x, str) for x in required_counters):
        findings.append("invalid_required_runtime_counters_policy")
        required_counters = ["auth_failures_by_token", "token_requests", "job_replays"]

    state: dict[str, Any] = {}
    if not state_path.exists():
        findings.append("runtime_state_missing")
    else:
        loaded = json.loads(state_path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            findings.append("runtime_state_not_object")
        else:
            state = loaded

    quotas = _as_dict(state.get("quotas", {}))
    if not quotas:
        findings.append("missing_or_invalid_quotas")
    for key in _REQUIRED_QUOTA_KEYS:
        value = quotas.get(key)
        if not isinstance(value, dict):
            findings.append(f"missing_quota_dict:{key}")

    missing_required_counters = sorted(
        key for key in required_counters if not isinstance(quotas.get(str(key), None), dict)
    )
    if missing_required_counters:
        findings.append(f"missing_required_runtime_counters:{','.join(missing_required_counters)}")

    summary = {
        "state_path": str(state_path.relative_to(ROOT)).replace("\\", "/"),
        "required_quota_dicts": len(_REQUIRED_QUOTA_KEYS),
        "required_runtime_counters": required_counters,
        "quota_keys_present": sorted(quotas.keys()),
        "missing_required_counters_count": len(missing_required_counters),
    }
    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": summary,
        "metadata": {"gate": "runtime_api_state_schema_gate"},
    }
    out = evidence_root() / "security" / "runtime_api_state_schema_gate.json"
    write_json_report(out, report)
    print(f"RUNTIME_API_STATE_SCHEMA_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
