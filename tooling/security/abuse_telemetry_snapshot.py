#!/usr/bin/env python3
from __future__ import annotations

import json
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
    try:
        job = svc.submit_job(payload=payload, token="telemetry-token", scope="jobs:write")
        svc.status(job["job_id"], token="telemetry-token", scope="jobs:read")
    except Exception:
        pass
    try:
        svc.submit_job(payload=payload, token="role:viewer", scope="jobs:write")
    except Exception:
        pass

    print(f"ABUSE_TELEMETRY_SNAPSHOT: {state_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
