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

BASELINE_PATH = ROOT / "governance" / "security" / "abuse_telemetry_threshold_baseline.json"
THRESHOLD_APPROVAL_PATH = ROOT / "governance" / "security" / "abuse_threshold_change_approval.json"
THRESHOLD_KEYS = ("max_distinct_tokens", "max_auth_failures_per_token", "max_failure_spike")


def _audit_log_path_for_state(state_path: Path) -> Path:
    return state_path.parent / "audit.log.jsonl"


def _extract_role(token: str) -> str:
    if not token.startswith("role:"):
        return ""
    role = token.split(":", 1)[1].strip()
    return role


def _role_dimension_counts(*, token_requests: dict[str, Any], auth_failures: dict[str, Any]) -> tuple[dict[str, int], list[str]]:
    role_counts: dict[str, int] = {}
    findings: list[str] = []
    role_tokens_seen = False
    tokens = set(token_requests.keys()) | set(auth_failures.keys())
    for token in tokens:
        if not isinstance(token, str):
            continue
        role = _extract_role(token)
        if role:
            role_tokens_seen = True
            role_counts[role] = role_counts.get(role, 0) + 1
        elif token.startswith("role:"):
            role_tokens_seen = True
            findings.append("invalid_role_token_dimension:empty_role")
    if role_tokens_seen and not role_counts:
        findings.append("missing_token_role_dimension")
    return role_counts, findings


def _source_dimension_counts(audit_log_path: Path) -> tuple[dict[str, int], list[str]]:
    source_counts: dict[str, int] = {}
    findings: list[str] = []
    if not audit_log_path.exists():
        return source_counts, findings
    missing_kind = 0
    parsed = 0
    for line in audit_log_path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw:
            continue
        try:
            event = json.loads(raw)
        except Exception:
            findings.append("invalid_audit_log_json")
            continue
        if not isinstance(event, dict):
            findings.append("invalid_audit_log_event_shape")
            continue
        parsed += 1
        kind = str(event.get("role_token_kind", "")).strip()
        if not kind:
            missing_kind += 1
            continue
        source_counts[kind] = source_counts.get(kind, 0) + 1
    if parsed > 0 and source_counts == {}:
        findings.append("missing_token_source_dimension")
    elif missing_kind > 0:
        findings.append(f"missing_role_token_kind_in_audit_events:{missing_kind}")
    return source_counts, findings


def _as_int(value: Any, default: int = 0) -> int:
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except Exception:
        return default


def _profile_thresholds(doc: dict[str, Any], profile: str) -> dict[str, int]:
    profile_policy = doc.get("profiles", {}).get(profile, {}) if isinstance(doc.get("profiles"), dict) else {}
    if not isinstance(profile_policy, dict):
        profile_policy = {}
    return {
        key: _as_int(profile_policy.get(key, doc.get(key, 0)), _as_int(doc.get(key, 0), 0))
        for key in THRESHOLD_KEYS
    }


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _staged_rollout_evidence_findings(approval: dict[str, Any]) -> tuple[list[str], list[str]]:
    findings: list[str] = []
    rel_paths: list[str] = []
    raw_paths = approval.get("staged_rollout_evidence", [])
    if not isinstance(raw_paths, list) or not raw_paths:
        return ["missing_staged_rollout_evidence"], rel_paths
    for item in raw_paths:
        rel = str(item).strip()
        if not rel:
            findings.append("invalid_staged_rollout_evidence_entry")
            continue
        rel_paths.append(rel)
        evidence_path = ROOT / rel
        if not evidence_path.exists():
            findings.append(f"missing_staged_rollout_evidence:{rel}")
    return findings, rel_paths


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

    policy = _load_json(policy_path)
    if not policy:
        raise ValueError("invalid abuse telemetry policy")

    state_path = ROOT / str(policy.get("runtime_api_state_path", "")).strip()
    profile = os.environ.get("GLYPHSER_ENV", "").strip().lower() or "ci"
    resolved_thresholds = _profile_thresholds(policy, profile)
    max_distinct_tokens = resolved_thresholds["max_distinct_tokens"] or 200
    max_auth_failures_per_token = resolved_thresholds["max_auth_failures_per_token"] or 20
    max_failure_spike = resolved_thresholds["max_failure_spike"] or 100
    findings: list[str] = []
    summary: dict[str, Any] = {
        "state_path": str(state_path.relative_to(ROOT)).replace("\\", "/"),
        "max_distinct_tokens": max_distinct_tokens,
        "max_auth_failures_per_token": max_auth_failures_per_token,
        "max_failure_spike": max_failure_spike,
        "profile": profile,
    }

    if BASELINE_PATH.exists():
        baseline = _load_json(BASELINE_PATH)
        baseline_thresholds = _profile_thresholds(baseline, profile)
        loosened: list[str] = []
        for key in THRESHOLD_KEYS:
            base = int(baseline_thresholds.get(key, 0))
            current = int(resolved_thresholds.get(key, 0))
            if current > base:
                loosened.append(f"{profile}:{key}:{base}->{current}")
        if loosened:
            approval_valid = False
            approval_rollout_findings: list[str] = []
            approval_rollout_paths: list[str] = []
            if THRESHOLD_APPROVAL_PATH.exists() and THRESHOLD_APPROVAL_PATH.with_suffix(".json.sig").exists():
                approval_sig = THRESHOLD_APPROVAL_PATH.with_suffix(".json.sig").read_text(encoding="utf-8").strip()
                if approval_sig:
                    approval_key = current_key(strict=args.strict_key)
                    if verify_file(THRESHOLD_APPROVAL_PATH, approval_sig, key=approval_key):
                        approval = _load_json(THRESHOLD_APPROVAL_PATH)
                        approvals = approval.get("approved_relaxations", []) if isinstance(approval, dict) else []
                        approvals_set = {str(item).strip() for item in approvals if str(item).strip()}
                        rollout_findings, rollout_paths = _staged_rollout_evidence_findings(approval)
                        approval_rollout_findings = rollout_findings
                        approval_rollout_paths = rollout_paths
                        approval_valid = all(item in approvals_set for item in loosened) and not rollout_findings
            if not approval_valid:
                findings.extend(f"threshold_loosened_without_signed_approval:{item}" for item in loosened)
                findings.extend(f"threshold_relaxation_missing_rollout_evidence:{item}" for item in approval_rollout_findings)
            summary["threshold_relaxations"] = loosened
            summary["threshold_relaxation_rollout_evidence"] = approval_rollout_paths

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

        role_dimensions, role_findings = _role_dimension_counts(token_requests=token_requests, auth_failures=auth_failures)
        source_dimensions, source_findings = _source_dimension_counts(_audit_log_path_for_state(state_path))
        summary["token_role_dimensions"] = role_dimensions
        summary["token_source_dimensions"] = source_dimensions
        findings.extend(role_findings)
        findings.extend(source_findings)

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
