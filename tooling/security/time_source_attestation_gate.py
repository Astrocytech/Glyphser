#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
load_stage_s_policy = importlib.import_module("tooling.security.stage_s_policy").load_stage_s_policy
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report
clock_consistency_violation = importlib.import_module("tooling.security.report_io").clock_consistency_violation


def main(argv: list[str] | None = None) -> int:
    _ = argv
    cfg = load_stage_s_policy().get("time_attestation", {})
    max_skew = int(cfg.get("max_skew_seconds", 300))
    env_var = str(cfg.get("environment_var", "GLYPHSER_ENV"))
    env_name = os.environ.get(env_var, os.environ.get("GLYPHSER_ENVIRONMENT", "local")).strip().lower() or "local"
    by_env = cfg.get("max_skew_seconds_by_environment", {})
    if isinstance(by_env, dict):
        raw_env_skew = by_env.get(env_name)
        if isinstance(raw_env_skew, int):
            max_skew = raw_env_skew
    stale_threshold = int(cfg.get("stale_clock_threshold_seconds", max_skew))
    trusted_env = str(cfg.get("trusted_unix_time_env", "GLYPHSER_TRUSTED_UNIX_TIME"))

    system_unix = time.time()
    now = datetime.now(UTC)
    trusted_raw = os.environ.get(trusted_env, "").strip()
    findings: list[str] = []
    clock_issue = clock_consistency_violation(now)
    if clock_issue:
        findings.append(clock_issue)
    trusted_unix = None
    skew_seconds = 0
    if trusted_raw:
        try:
            trusted_unix = float(trusted_raw)
            skew_seconds = int(abs(system_unix - trusted_unix))
            if skew_seconds > max_skew:
                findings.append(f"clock_skew_exceeds_threshold:{skew_seconds}")
        except ValueError:
            findings.append("invalid_trusted_unix_time")

    stale_clock_detected = bool(trusted_unix is not None and skew_seconds > stale_threshold)
    stale_clock_artifact = {
        "status": "FAIL" if stale_clock_detected else "PASS",
        "findings": [f"stale_clock_detected:skew_seconds:{skew_seconds}:threshold_seconds:{stale_threshold}"]
        if stale_clock_detected
        else [],
        "summary": {
            "observed_utc": now.isoformat(),
            "observed_unix": system_unix,
            "trusted_unix_time_env": trusted_env,
            "trusted_unix": trusted_unix,
            "skew_seconds": skew_seconds,
            "stale_clock_threshold_seconds": stale_threshold,
            "stale_clock_detected": stale_clock_detected,
            "remediation_guidance": [
                "Verify host time synchronization service (chrony/ntpd/systemd-timesyncd) is healthy and synced.",
                f"Validate `{trusted_env}` uses a recent trusted timestamp source before running security gates.",
                "If skew persists, quarantine the runner and escalate via governance/security/OPERATIONS.md incident flow.",
            ],
        },
        "metadata": {"gate": "time_source_attestation_gate", "artifact": "stale_clock_detection"},
    }

    attestation = {
        "observed_utc": now.isoformat(),
        "observed_unix": system_unix,
        "trusted_unix": trusted_unix,
        "skew_seconds": skew_seconds,
        "max_skew_seconds": max_skew,
        "environment": env_name,
        "environment_var": env_var,
    }

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": attestation,
        "metadata": {"gate": "time_source_attestation_gate"},
    }
    sec = evidence_root() / "security"
    out = sec / "time_source_attestation_gate.json"
    stale_out = sec / "stale_clock_detection_artifact.json"
    write_json_report(out, report)
    write_json_report(stale_out, stale_clock_artifact)
    print(f"TIME_SOURCE_ATTESTATION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
