#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report
replay_harness = importlib.import_module("tooling.security.deterministic_replay_harness")


def _load(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Detect non-deterministic field drift in static replay reports by recomputing and comparing fields."
    )
    parser.add_argument("--run-dir", required=True, help="Saved run directory used by deterministic replay harness.")
    args = parser.parse_args([] if argv is None else argv)

    run_dir = Path(args.run_dir)
    if not run_dir.is_absolute():
        run_dir = (ROOT / run_dir).resolve()
    replay_report_path = run_dir / "security" / "deterministic_replay_harness.json"

    findings: list[str] = []
    checks: list[dict[str, Any]] = []

    persisted = _load(replay_report_path)
    if persisted is None:
        findings.append("missing_or_invalid_replay_harness_report")
    else:
        expected_findings, expected_checks = replay_harness.evaluate_run_dir(run_dir)
        persisted_findings = persisted.get("findings", [])
        if not isinstance(persisted_findings, list):
            persisted_findings = []
            findings.append("invalid_replay_harness_findings_shape")
        if persisted_findings != expected_findings:
            findings.append("nondeterministic_field_drift:findings")

        persisted_checks = persisted.get("checks", [])
        if not isinstance(persisted_checks, list):
            persisted_checks = []
            findings.append("invalid_replay_harness_checks_shape")
        if persisted_checks != expected_checks:
            findings.append("nondeterministic_field_drift:checks")

        summary = persisted.get("summary", {})
        if not isinstance(summary, dict):
            summary = {}
            findings.append("invalid_replay_harness_summary_shape")
        expected_checked = len(expected_checks)
        expected_mismatches = len([item for item in expected_checks if not bool(item.get("ok", False))])
        if int(summary.get("checked_reports", -1)) != expected_checked:
            findings.append("nondeterministic_field_drift:summary.checked_reports")
        if int(summary.get("mismatch_count", -1)) != expected_mismatches:
            findings.append("nondeterministic_field_drift:summary.mismatch_count")

        checks = [
            {
                "field": "findings",
                "ok": persisted_findings == expected_findings,
            },
            {
                "field": "checks",
                "ok": persisted_checks == expected_checks,
            },
            {
                "field": "summary.checked_reports",
                "ok": int(summary.get("checked_reports", -1)) == expected_checked,
            },
            {
                "field": "summary.mismatch_count",
                "ok": int(summary.get("mismatch_count", -1)) == expected_mismatches,
            },
        ]

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"run_dir": str(run_dir), "compared_fields": len(checks)},
        "metadata": {"gate": "replay_nondeterministic_field_drift_gate"},
        "checks": checks,
    }
    out = evidence_root() / "security" / "replay_nondeterministic_field_drift_gate.json"
    write_json_report(out, report)
    print(f"REPLAY_NONDETERMINISTIC_FIELD_DRIFT_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
