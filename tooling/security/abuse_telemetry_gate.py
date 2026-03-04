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


def _as_int(value: Any, default: int = 0) -> int:
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except Exception:
        return default


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = json.loads((ROOT / "governance" / "security" / "abuse_telemetry_policy.json").read_text(encoding="utf-8"))
    if not isinstance(policy, dict):
        raise ValueError("invalid abuse telemetry policy")

    state_path = ROOT / str(policy.get("runtime_api_state_path", "")).strip()
    max_distinct_tokens = _as_int(policy.get("max_distinct_tokens", 200), 200)
    max_auth_failures_per_token = _as_int(policy.get("max_auth_failures_per_token", 20), 20)
    findings: list[str] = []
    summary: dict[str, Any] = {
        "state_path": str(state_path.relative_to(ROOT)).replace("\\", "/"),
        "max_distinct_tokens": max_distinct_tokens,
        "max_auth_failures_per_token": max_auth_failures_per_token,
    }

    if not state_path.exists():
        findings.append("runtime api state file missing")
    else:
        state = json.loads(state_path.read_text(encoding="utf-8"))
        quotas = state.get("quotas", {}) if isinstance(state, dict) else {}
        token_requests = quotas.get("token_requests", {}) if isinstance(quotas, dict) else {}
        auth_failures = quotas.get("auth_failures_by_token", {}) if isinstance(quotas, dict) else {}
        if not isinstance(token_requests, dict):
            token_requests = {}
        if not isinstance(auth_failures, dict):
            auth_failures = {}

        distinct_tokens = len(token_requests)
        summary["distinct_tokens"] = distinct_tokens
        summary["auth_failures_by_token"] = auth_failures
        if distinct_tokens > max_distinct_tokens:
            findings.append(f"token spray suspected: {distinct_tokens} distinct tokens")

        offenders = sorted(
            token
            for token, count in auth_failures.items()
            if isinstance(token, str) and _as_int(count, 0) > max_auth_failures_per_token
        )
        if offenders:
            findings.append(f"repeated auth failures over threshold for: {', '.join(offenders)}")

    payload = {"status": "PASS" if not findings else "FAIL", "findings": findings, "summary": summary}
    out = evidence_root() / "security" / "abuse_telemetry.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"ABUSE_TELEMETRY_GATE: {payload['status']}")
    print(f"Report: {out}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
