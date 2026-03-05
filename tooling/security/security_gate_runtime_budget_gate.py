#!/usr/bin/env python3
from __future__ import annotations

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

POLICY = ROOT / "governance" / "security" / "security_gate_runtime_budget_policy.json"
HISTORY = ROOT / "evidence" / "security" / "security_gate_runtime_history.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _script_from_cmd(cmd: list[Any]) -> str:
    if len(cmd) >= 2 and isinstance(cmd[1], str):
        return cmd[1]
    return str(cmd[0]) if cmd else ""


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    alarms: list[dict[str, Any]] = []

    if not POLICY.exists():
        findings.append("missing_security_gate_runtime_budget_policy")
        policy = {}
    else:
        try:
            policy = _load_json(POLICY)
        except Exception:
            findings.append("invalid_security_gate_runtime_budget_policy")
            policy = {}

    default_budget = float(policy.get("default_max_runtime_sec", 120.0)) if isinstance(policy, dict) else 120.0
    budget_map_raw = policy.get("per_gate_max_runtime_sec", {}) if isinstance(policy, dict) else {}
    budget_map = {str(k): float(v) for k, v in budget_map_raw.items()} if isinstance(budget_map_raw, dict) else {}
    required_budget_gates_raw = policy.get("required_budget_gates", []) if isinstance(policy, dict) else []
    required_budget_gates = (
        [str(item) for item in required_budget_gates_raw if isinstance(item, str) and str(item).strip()]
        if isinstance(required_budget_gates_raw, list)
        else []
    )
    spike_multiplier = float(policy.get("trend_spike_multiplier", 2.5)) if isinstance(policy, dict) else 2.5
    min_spike_sec = float(policy.get("min_spike_seconds", 10.0)) if isinstance(policy, dict) else 10.0
    history_window = int(policy.get("history_window", 30)) if isinstance(policy, dict) else 30
    if history_window < 5:
        history_window = 30

    super_path = evidence_root() / "security" / "security_super_gate.json"
    if not super_path.exists():
        findings.append("missing_security_super_gate_report")
        results: list[dict[str, Any]] = []
    else:
        try:
            payload = _load_json(super_path)
            raw = payload.get("results", []) if isinstance(payload, dict) else []
            results = [item for item in raw if isinstance(item, dict)] if isinstance(raw, list) else []
        except Exception:
            findings.append("invalid_security_super_gate_report")
            results = []

    history_payload: dict[str, Any] = {}
    if HISTORY.exists():
        try:
            history_payload = _load_json(HISTORY)
        except Exception:
            history_payload = {}
            findings.append("invalid_security_gate_runtime_history")
    history_raw = history_payload.get("gate_runtimes", {}) if isinstance(history_payload, dict) else {}
    history: dict[str, list[float]] = {}
    if isinstance(history_raw, dict):
        for key, values in history_raw.items():
            if not isinstance(key, str) or not isinstance(values, list):
                continue
            history[key] = [float(v) for v in values if isinstance(v, (int, float)) and float(v) >= 0.0]

    checked = 0
    spikes = 0
    for script in required_budget_gates:
        if script not in budget_map:
            findings.append(f"missing_per_gate_budget:{script}")

    for item in results:
        cmd = item.get("cmd", [])
        if not isinstance(cmd, list):
            continue
        script = _script_from_cmd(cmd)
        if not script:
            continue
        runtime = item.get("runtime_seconds")
        if not isinstance(runtime, (int, float)):
            findings.append(f"missing_runtime_seconds:{script}")
            continue
        runtime_s = float(runtime)
        checked += 1

        budget = float(budget_map.get(script, default_budget))
        if runtime_s > budget:
            findings.append(f"runtime_budget_exceeded:{script}:{runtime_s:.3f}s>{budget:.3f}s")
            alarms.append(
                {
                    "alarm": "runtime_budget_exceeded",
                    "script": script,
                    "current_runtime_sec": runtime_s,
                    "budget_sec": budget,
                }
            )

        prev = history.get(script, [])
        if prev:
            avg_prev = sum(prev) / len(prev)
            if runtime_s > avg_prev * spike_multiplier and (runtime_s - avg_prev) >= min_spike_sec:
                spikes += 1
                findings.append(
                    f"runtime_spike_detected:{script}:current:{runtime_s:.3f}s:baseline:{avg_prev:.3f}s:multiplier:{spike_multiplier:.2f}"
                )
                alarms.append(
                    {
                        "alarm": "runtime_spike_detected",
                        "script": script,
                        "current_runtime_sec": runtime_s,
                        "baseline_runtime_sec": avg_prev,
                        "spike_multiplier": spike_multiplier,
                    }
                )
        updated = (prev + [runtime_s])[-history_window:]
        history[script] = updated

    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    HISTORY.write_text(json.dumps({"schema_version": 1, "gate_runtimes": history}, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    history_snapshot = evidence_root() / "security" / "security_gate_runtime_history.json"
    history_snapshot.parent.mkdir(parents=True, exist_ok=True)
    history_snapshot.write_text(
        json.dumps({"schema_version": 1, "gate_runtimes": history}, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "checked_gates": checked,
            "default_budget_sec": default_budget,
            "spike_count": spikes,
            "history_window": history_window,
            "required_budget_gates": len(required_budget_gates),
            "alarm_count": len(alarms),
        },
        "metadata": {"gate": "security_gate_runtime_budget_gate"},
        "regression_alarms": alarms,
    }
    out = evidence_root() / "security" / "security_gate_runtime_budget_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_GATE_RUNTIME_BUDGET_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
