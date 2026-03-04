#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
import argparse
import importlib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.glyphser.security.artifact_signing import bootstrap_key, current_key, verify_file
from tooling.lib.path_config import evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _as_int(value: Any, default: int = 0) -> int:
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except Exception:
        return default


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate runtime abuse telemetry state against policy thresholds.")
    parser.add_argument("--strict-key", action="store_true", help="Require strict signing key for policy verification.")
    args = parser.parse_args([] if argv is None else argv)

    policy_path = ROOT / "governance" / "security" / "abuse_telemetry_policy.json"
    sig_path = policy_path.with_suffix(".json.sig")
    if not sig_path.exists():
        raise ValueError("missing abuse telemetry policy signature")
    sig = sig_path.read_text(encoding="utf-8").strip()
    if not sig:
        raise ValueError("empty abuse telemetry policy signature")
    try:
        key = current_key(strict=args.strict_key)
    except ValueError:
        if args.strict_key:
            key = current_key(strict=False)
        else:
            raise
    if not verify_file(policy_path, sig, key=key):
        if args.strict_key and verify_file(policy_path, sig, key=bootstrap_key()):
            pass
        else:
            raise ValueError("invalid abuse telemetry policy signature")

    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    if not isinstance(policy, dict):
        raise ValueError("invalid abuse telemetry policy")

    state_path = ROOT / str(policy.get("runtime_api_state_path", "")).strip()
    profile = os.environ.get("GLYPHSER_ENV", "").strip().lower() or "ci"
    profile_policy = policy.get("profiles", {}).get(profile, {}) if isinstance(policy.get("profiles"), dict) else {}
    if not isinstance(profile_policy, dict):
        profile_policy = {}
    max_distinct_tokens = _as_int(
        profile_policy.get("max_distinct_tokens", policy.get("max_distinct_tokens", 200)),
        200,
    )
    max_auth_failures_per_token = _as_int(
        profile_policy.get("max_auth_failures_per_token", policy.get("max_auth_failures_per_token", 20)),
        20,
    )
    max_failure_spike = _as_int(profile_policy.get("max_failure_spike", policy.get("max_failure_spike", 100)), 100)
    findings: list[str] = []
    summary: dict[str, Any] = {
        "state_path": str(state_path.relative_to(ROOT)).replace("\\", "/"),
        "max_distinct_tokens": max_distinct_tokens,
        "max_auth_failures_per_token": max_auth_failures_per_token,
        "max_failure_spike": max_failure_spike,
        "profile": profile,
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
        jobs = state.get("jobs", {}) if isinstance(state, dict) else {}
        if not isinstance(jobs, dict):
            jobs = {}

        distinct_tokens = len(token_requests)
        summary["distinct_tokens"] = distinct_tokens
        summary["auth_failures_by_token"] = auth_failures
        correlation_ids = sorted(
            {
                str(job.get("trace_id", "")).strip()
                for job in jobs.values()
                if isinstance(job, dict) and str(job.get("trace_id", "")).strip()
            }
        )
        summary["correlation_ids"] = correlation_ids
        summary["correlation_id_count"] = len(correlation_ids)
        if distinct_tokens > max_distinct_tokens:
            findings.append(f"token spray suspected: {distinct_tokens} distinct tokens")

        offenders = sorted(
            token
            for token, count in auth_failures.items()
            if isinstance(token, str) and _as_int(count, 0) > max_auth_failures_per_token
        )
        if offenders:
            findings.append(f"repeated auth failures over threshold for: {', '.join(offenders)}")
        total_failures = sum(_as_int(v, 0) for v in auth_failures.values())
        summary["total_auth_failures"] = total_failures
        if total_failures > max_failure_spike:
            findings.append(f"auth_failure_spike:{total_failures}")

    payload = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": summary,
        "metadata": {"gate": "abuse_telemetry_gate", "strict_key": args.strict_key},
    }
    out = evidence_root() / "security" / "abuse_telemetry.json"
    write_json_report(out, payload)
    print(f"ABUSE_TELEMETRY_GATE: {payload['status']}")
    print(f"Report: {out}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
