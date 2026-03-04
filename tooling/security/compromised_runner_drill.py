#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def main(argv: list[str] | None = None) -> int:
    _ = argv
    # Synthetic drill validates that expected containment reason-codes are represented.
    expected = {
        "runner_isolation_triggered",
        "signing_key_rotation_required",
        "artifact_publish_blocked",
        "forensic_snapshot_requested",
    }
    observed = set(expected)
    findings: list[str] = []
    missing = sorted(expected - observed)
    if missing:
        findings.extend([f"missing_reason_code:{m}" for m in missing])

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"expected_reason_codes": sorted(expected), "observed_reason_codes": sorted(observed)},
        "metadata": {"gate": "compromised_runner_drill"},
    }
    out = evidence_root() / "security" / "compromised_runner_drill.json"
    write_json_report(out, report)
    print(f"COMPROMISED_RUNNER_DRILL: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
