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


def main(argv: list[str] | None = None) -> int:
    _ = argv
    cfg = load_stage_s_policy().get("time_attestation", {})
    max_skew = int(cfg.get("max_skew_seconds", 300))
    trusted_env = str(cfg.get("trusted_unix_time_env", "GLYPHSER_TRUSTED_UNIX_TIME"))

    system_unix = time.time()
    trusted_raw = os.environ.get(trusted_env, "").strip()
    findings: list[str] = []
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

    attestation = {
        "observed_utc": datetime.now(UTC).isoformat(),
        "observed_unix": system_unix,
        "trusted_unix": trusted_unix,
        "skew_seconds": skew_seconds,
        "max_skew_seconds": max_skew,
    }

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": attestation,
        "metadata": {"gate": "time_source_attestation_gate"},
    }
    out = evidence_root() / "security" / "time_source_attestation_gate.json"
    write_json_report(out, report)
    print(f"TIME_SOURCE_ATTESTATION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
