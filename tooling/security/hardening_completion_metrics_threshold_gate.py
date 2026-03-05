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

THRESHOLDS = ROOT / "governance" / "security" / "hardening_metrics_thresholds.json"
METRICS = ROOT / "evidence" / "security" / "hardening_completion_metrics.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _metric_value(payload: dict[str, Any], key: str) -> float | None:
    metrics = payload.get("metrics", {}) if isinstance(payload.get("metrics", {}), dict) else {}
    node = metrics.get(key, {}) if isinstance(metrics.get(key, {}), dict) else {}
    value = node.get("value")
    try:
        return float(value)
    except Exception:
        return None


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    breaches: list[dict[str, Any]] = []

    if not THRESHOLDS.exists():
        findings.append("missing_hardening_metrics_thresholds")
        thresholds: dict[str, Any] = {}
    else:
        thresholds = _load_json(THRESHOLDS)

    if not METRICS.exists():
        findings.append("missing_hardening_completion_metrics")
        metrics_payload: dict[str, Any] = {}
    else:
        metrics_payload = _load_json(METRICS)

    rules = thresholds.get("thresholds", {}) if isinstance(thresholds.get("thresholds", {}), dict) else {}
    for metric_name, rule in rules.items():
        if not isinstance(rule, dict):
            findings.append(f"invalid_threshold_rule:{metric_name}")
            continue
        value = _metric_value(metrics_payload, str(metric_name))
        if value is None:
            findings.append(f"missing_metric_value:{metric_name}")
            continue

        low = rule.get("min")
        high = rule.get("max")
        breached = False
        threshold_value: float | None = None
        comparator = ""
        if low is not None:
            try:
                lowf = float(low)
                if value < lowf:
                    breached = True
                    threshold_value = lowf
                    comparator = "min"
            except Exception:
                findings.append(f"invalid_threshold_min:{metric_name}")
                continue
        if high is not None and not breached:
            try:
                highf = float(high)
                if value > highf:
                    breached = True
                    threshold_value = highf
                    comparator = "max"
            except Exception:
                findings.append(f"invalid_threshold_max:{metric_name}")
                continue

        if breached:
            breaches.append(
                {
                    "metric": metric_name,
                    "value": value,
                    "threshold_type": comparator,
                    "threshold": threshold_value,
                    "severity": str(rule.get("severity", "warning")),
                    "message": str(rule.get("message", f"threshold_breach:{metric_name}")),
                }
            )

    status = "PASS"
    if breaches and not findings:
        status = "WARN"
    if findings:
        status = "FAIL"

    report = {
        "status": status,
        "findings": findings,
        "summary": {
            "metrics_checked": len(rules),
            "breaches": len(breaches),
        },
        "metadata": {"gate": "hardening_completion_metrics_threshold_gate"},
        "breaches": breaches,
    }
    out = evidence_root() / "security" / "hardening_completion_metrics_threshold_gate.json"
    write_json_report(out, report)
    print(f"HARDENING_COMPLETION_METRICS_THRESHOLD_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
