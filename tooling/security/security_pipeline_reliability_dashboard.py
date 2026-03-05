#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

HISTORY = ROOT / "evidence" / "security" / "security_pipeline_reliability_history.json"
POLICY = ROOT / "governance" / "security" / "security_workflow_reliability_budget_policy.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _failed_gates_from_super(report: dict[str, Any]) -> list[str]:
    results = report.get("results", []) if isinstance(report, dict) else []
    if not isinstance(results, list):
        return []
    failed: list[str] = []
    for item in results:
        if not isinstance(item, dict):
            continue
        if str(item.get("status", "")).upper() == "PASS":
            continue
        cmd = item.get("cmd", [])
        if isinstance(cmd, list) and len(cmd) >= 2 and isinstance(cmd[1], str):
            failed.append(cmd[1])
    return sorted(set(failed))


def _metrics(runs: list[dict[str, Any]]) -> tuple[float, float, int, int]:
    total_runs = len(runs)
    if total_runs == 0:
        return 0.0, 0.0, 0, 0

    all_gates = sorted({gate for run in runs for gate in run.get("failed_gates", []) if isinstance(gate, str)})
    resolved_streaks: list[int] = []
    flake_events = 0

    for gate in all_gates:
        streak = 0
        for idx, run in enumerate(runs):
            failed = gate in run.get("failed_gates", [])
            if failed:
                streak += 1
                continue
            if streak > 0:
                resolved_streaks.append(streak)
                if streak == 1 and idx > 0:
                    flake_events += 1
                streak = 0

    mttr_runs = (sum(resolved_streaks) / len(resolved_streaks)) if resolved_streaks else 0.0
    flake_rate = flake_events / total_runs
    current_open = len(runs[-1].get("failed_gates", [])) if runs else 0
    return mttr_runs, flake_rate, current_open, flake_events


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    super_path = sec / "security_super_gate.json"
    findings: list[str] = []

    if not super_path.exists():
        findings.append("missing_security_super_gate_report")
        failed = []
    else:
        try:
            failed = _failed_gates_from_super(_load_json(super_path))
        except Exception:
            failed = []
            findings.append("invalid_security_super_gate_report")

    history_payload: dict[str, Any] = {}
    if HISTORY.exists():
        try:
            history_payload = _load_json(HISTORY)
        except Exception:
            findings.append("invalid_security_pipeline_reliability_history")
            history_payload = {}

    runs_raw = history_payload.get("runs", []) if isinstance(history_payload, dict) else []
    runs = [item for item in runs_raw if isinstance(item, dict)] if isinstance(runs_raw, list) else []
    runs.append(
        {
            "run_id": str(os.environ.get("GITHUB_RUN_ID") or os.environ.get("CI_PIPELINE_ID") or f"local-{len(runs)+1}"),
            "failed_gates": failed,
        }
    )
    runs = runs[-120:]

    mttr_runs, flake_rate, current_open, flake_events = _metrics(runs)

    if POLICY.exists():
        try:
            policy = _load_json(POLICY)
        except Exception:
            policy = {}
            findings.append("invalid_reliability_budget_policy")
    else:
        policy = {}
    flake_budget_events = int(policy.get("flake_budget_events", 0) or 0) if isinstance(policy, dict) else 0
    max_open_gate_failures = int(policy.get("max_open_gate_failures", 0) or 0) if isinstance(policy, dict) else 0
    budget_remaining = flake_budget_events - flake_events if flake_budget_events > 0 else 0
    burn_down_pct = (
        100.0
        if flake_budget_events <= 0
        else round(max(0.0, min(1.0, budget_remaining / flake_budget_events)) * 100.0, 2)
    )
    if flake_budget_events > 0 and flake_events > flake_budget_events:
        findings.append(f"flake_budget_exceeded:{flake_events}:{flake_budget_events}")
    if max_open_gate_failures > 0 and current_open > max_open_gate_failures:
        findings.append(f"open_gate_failures_exceeded:{current_open}:{max_open_gate_failures}")

    history_doc = {"schema_version": 1, "runs": runs}
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    HISTORY.write_text(json.dumps(history_doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    snapshot = sec / "security_pipeline_reliability_history.json"
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    snapshot.write_text(json.dumps(history_doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report = {
        "status": "PASS" if not findings else "WARN",
        "findings": findings,
        "summary": {
            "runs_tracked": len(runs),
            "mttr_runs": round(mttr_runs, 3),
            "flake_rate": round(flake_rate, 5),
            "flake_events": flake_events,
            "current_open_gate_failures": current_open,
            "flake_budget_events": flake_budget_events,
            "flake_budget_remaining": budget_remaining,
            "flake_budget_burn_down_pct": burn_down_pct,
            "max_open_gate_failures": max_open_gate_failures,
        },
        "metadata": {"gate": "security_pipeline_reliability_dashboard"},
    }
    out = sec / "security_pipeline_reliability_dashboard.json"
    write_json_report(out, report)
    print("SECURITY_PIPELINE_RELIABILITY_DASHBOARD: PASS")
    print(f"Report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
