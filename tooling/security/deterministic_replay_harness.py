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

SUPER_GATE_REPORT = "security_super_gate.json"


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def _extract_report_name(result: dict[str, Any]) -> str:
    stdout = str(result.get("stdout", ""))
    for line in stdout.splitlines():
        text = line.strip()
        if not text.startswith("Report:"):
            continue
        return Path(text.split(":", 1)[1].strip()).name
    cmd = result.get("cmd", [])
    if isinstance(cmd, list) and len(cmd) >= 2:
        candidate = Path(str(cmd[1])).name
        if candidate.endswith(".py"):
            return f"{candidate[:-3]}.json"
    return "unknown.json"


def _recomputed_status(report_path: Path) -> str:
    payload = _load_json(report_path)
    if payload is None:
        return "MISSING" if not report_path.exists() else "INVALID"
    return str(payload.get("status", "UNKNOWN")).upper()


def evaluate_run_dir(run_dir: Path) -> tuple[list[str], list[dict[str, str | bool]]]:
    security_dir = run_dir / "security"
    findings: list[str] = []
    checks: list[dict[str, str | bool]] = []

    super_gate_path = security_dir / SUPER_GATE_REPORT
    super_gate = _load_json(super_gate_path)
    if super_gate is None:
        findings.append("missing_or_invalid_saved_super_gate_report")
        return findings, checks

    results = super_gate.get("results", [])
    if not isinstance(results, list):
        findings.append("saved_super_gate_results_not_list")
        return findings, checks

    for item in results:
        if not isinstance(item, dict):
            findings.append("invalid_saved_super_gate_result_entry")
            continue
        report_name = _extract_report_name(item)
        report_path = security_dir / report_name
        recorded = str(item.get("status", "UNKNOWN")).upper()
        recomputed = _recomputed_status(report_path)
        ok = recorded == recomputed
        checks.append(
            {
                "report": report_name,
                "recorded_status": recorded,
                "recomputed_status": recomputed,
                "ok": ok,
            }
        )
        if not ok:
            findings.append(f"replay_status_mismatch:report:{report_name}:recorded:{recorded}:recomputed:{recomputed}")
    return findings, checks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Replay a saved security run directory and compare recomputed gate statuses to recorded statuses."
    )
    parser.add_argument("--run-dir", required=True, help="Path to a saved run directory containing security artifacts.")
    args = parser.parse_args([] if argv is None else argv)

    run_dir = Path(args.run_dir)
    if not run_dir.is_absolute():
        run_dir = (ROOT / run_dir).resolve()
    findings, checks = evaluate_run_dir(run_dir)

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "run_dir": str(run_dir),
            "checked_reports": len(checks),
            "mismatch_count": len([item for item in checks if not bool(item.get("ok", False))]),
        },
        "metadata": {"gate": "deterministic_replay_harness"},
        "checks": checks,
    }
    out = evidence_root() / "security" / "deterministic_replay_harness.json"
    write_json_report(out, report)
    print(f"DETERMINISTIC_REPLAY_HARNESS: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
