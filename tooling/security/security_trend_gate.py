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


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    current_path = sec / "security_slo_report.json"
    hist_path = sec / "security_slo_history.json"
    current = json.loads(current_path.read_text(encoding="utf-8")) if current_path.exists() else {}
    history = json.loads(hist_path.read_text(encoding="utf-8")) if hist_path.exists() else {"values": []}
    values = history.get("values", []) if isinstance(history, dict) else []
    if not isinstance(values, list):
        values = []
    curr = float(current.get("summary", {}).get("pass_rate", 0.0)) if isinstance(current, dict) else 0.0
    prev = float(values[-1]) if values else curr
    values.append(curr)
    history = {"values": values[-30:]}
    hist_path.write_text(json.dumps(history, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    findings: list[str] = []
    if curr + 0.05 < prev:
        findings.append(f"security_trend_degrading:{prev:.3f}->{curr:.3f}")
    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"previous": prev, "current": curr},
        "metadata": {"gate": "security_trend_gate"},
    }
    out = sec / "security_trend_gate.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"SECURITY_TREND_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
