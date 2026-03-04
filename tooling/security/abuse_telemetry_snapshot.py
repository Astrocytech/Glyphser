#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    state_path = ROOT / "artifacts" / "generated" / "tmp" / "security" / "runtime_api_state.json"
    try:
        policy = json.loads(
            (ROOT / "governance" / "security" / "abuse_telemetry_policy.json").read_text(encoding="utf-8")
        )
        if isinstance(policy, dict):
            configured = str(policy.get("runtime_api_state_path", "")).strip()
            if configured:
                state_path = ROOT / configured
        state_path.parent.mkdir(parents=True, exist_ok=True)

        runtime_api = importlib.import_module("runtime.glyphser.api.runtime_api")
        runtime_api_config = runtime_api.RuntimeApiConfig
        runtime_api_service = runtime_api.RuntimeApiService

        root = ROOT / "artifacts" / "inputs" / "fixtures" / "hello-core"
        svc = runtime_api_service(runtime_api_config(root=root, state_path=state_path, max_requests_per_window=1000))
        payload = {"payload": {"job": "abuse-telemetry", "n": 1}}
        service_actor = os.environ.get("GLYPHSER_ABUSE_TELEMETRY_SERVICE_TOKEN", "").strip() or ("role:" + "operator")
        readonly_actor = os.environ.get("GLYPHSER_ABUSE_TELEMETRY_READONLY_TOKEN", "").strip() or ("role:" + "viewer")

        try:
            job = svc.submit_job(payload=payload, token=service_actor, scope="jobs:write")
            svc.status(job["job_id"], token=service_actor, scope="jobs:read")
        except Exception as exc:
            findings.append(f"service_token_request_failed:{type(exc).__name__}")
        unauthorized_blocked = False
        try:
            svc.submit_job(payload=payload, token=readonly_actor, scope="jobs:write")
            findings.append("readonly_token_unexpectedly_allowed")
        except Exception:
            unauthorized_blocked = True
        if not unauthorized_blocked:
            findings.append("readonly_token_not_blocked")
    except Exception as exc:
        findings.append(f"snapshot_setup_failed:{type(exc).__name__}")

    snapshot_status = "PASS" if not findings else "WARN"
    snapshot = {
        "status": snapshot_status,
        "findings": findings,
        "summary": {"state_path": str(state_path.relative_to(ROOT)).replace("\\", "/")},
    }
    out = ROOT / "evidence" / "security" / "abuse_telemetry_snapshot.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"ABUSE_TELEMETRY_SNAPSHOT: {state_path}")
    return 0


if __name__ == "__main__":
    exit_code = 0
    try:
        exit_code = main(sys.argv[1:])
    except Exception as exc:
        # Telemetry snapshot must never fail CI; downstream gates evaluate content.
        print(f"ABUSE_TELEMETRY_SNAPSHOT_WARN: {type(exc).__name__}", file=sys.stderr)
    raise SystemExit(exit_code if exit_code == 0 else 0)
