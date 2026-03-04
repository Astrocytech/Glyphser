#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.glyphser.api.runtime_api import RuntimeApiConfig, RuntimeApiService


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = json.loads((ROOT / "governance" / "security" / "abuse_telemetry_policy.json").read_text(encoding="utf-8"))
    if not isinstance(policy, dict):
        raise ValueError("invalid abuse telemetry policy")
    state_path = ROOT / str(policy.get("runtime_api_state_path", "")).strip()
    state_path.parent.mkdir(parents=True, exist_ok=True)

    root = ROOT / "artifacts" / "inputs" / "fixtures" / "hello-core"
    svc = RuntimeApiService(RuntimeApiConfig(root=root, state_path=state_path, max_requests_per_window=1000))
    payload = {"payload": {"job": "abuse-telemetry", "n": 1}}
    service_token = os.environ.get("GLYPHSER_ABUSE_TELEMETRY_SERVICE_TOKEN", "telemetry-service")
    readonly_token = os.environ.get("GLYPHSER_ABUSE_TELEMETRY_READONLY_TOKEN", "readonly-role")
    findings: list[str] = []
    try:
        job = svc.submit_job(payload=payload, token=service_token, scope="jobs:write")
        svc.status(job["job_id"], token=service_token, scope="jobs:read")
    except Exception as exc:
        findings.append(f"service_token_request_failed:{type(exc).__name__}")
    unauthorized_blocked = False
    try:
        svc.submit_job(payload=payload, token=readonly_token, scope="jobs:write")
        findings.append("readonly_token_unexpectedly_allowed")
    except Exception:
        unauthorized_blocked = True
    if not unauthorized_blocked:
        findings.append("readonly_token_not_blocked")

    snapshot = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"state_path": str(state_path.relative_to(ROOT)).replace("\\", "/")},
    }
    out = ROOT / "evidence" / "security" / "abuse_telemetry_snapshot.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"ABUSE_TELEMETRY_SNAPSHOT: {state_path}")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
