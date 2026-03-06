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

write_json_report = importlib.import_module("tooling.security.report_io").write_json_report
SCAN_TOOLCHAIN_LOCK = ROOT / "tooling" / "security" / "security_toolchain_lock.json"
SCAN_TOOLS = ("bandit", "pip-audit", "semgrep", "setuptools")


def _toolchain_versions(findings: list[str]) -> dict[str, str]:
    if not SCAN_TOOLCHAIN_LOCK.exists():
        findings.append("missing_security_toolchain_lock")
        return {}
    try:
        payload = json.loads(SCAN_TOOLCHAIN_LOCK.read_text(encoding="utf-8"))
    except Exception:
        findings.append("invalid_security_toolchain_lock")
        return {}
    if not isinstance(payload, dict):
        findings.append("invalid_security_toolchain_lock")
        return {}
    versions: dict[str, str] = {}
    for tool in SCAN_TOOLS:
        entry = payload.get(tool)
        if not isinstance(entry, dict):
            findings.append(f"missing_scan_tool_version:{tool}")
            continue
        version = str(entry.get("version", "")).strip()
        if not version:
            findings.append(f"missing_scan_tool_version:{tool}")
            continue
        versions[tool] = version
    return versions


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    correlation_ids: list[str] = []
    toolchain_versions = _toolchain_versions(findings)
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
            trace_id = str(job.get("trace_id", "")).strip()
            if trace_id:
                correlation_ids.append(trace_id)
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
        "summary": {
            "state_path": str(state_path.relative_to(ROOT)).replace("\\", "/"),
            "correlation_ids": sorted(set(correlation_ids)),
            "toolchain_versions": toolchain_versions,
        },
    }
    out = ROOT / "evidence" / "security" / "abuse_telemetry_snapshot.json"
    write_json_report(out, snapshot)

    print(f"ABUSE_TELEMETRY_SNAPSHOT: {state_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
