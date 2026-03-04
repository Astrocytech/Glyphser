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

_REMEDIATION = {
    "security_trend_degrading": {
        "urgency": "high",
        "playbook": "governance/security/INCIDENT_RUNBOOKS.md",
        "suggested_actions": [
            "Inspect newly failing gate reports under evidence/security.",
            "Prioritize fixes for failing signature/attestation/security-super-gate controls.",
            "Open incident ticket if degradation persists for 2+ runs.",
        ],
    }
}


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
    alerts: list[dict[str, object]] = []
    if curr + 0.05 < prev:
        code = "security_trend_degrading"
        findings.append(f"{code}:{prev:.3f}->{curr:.3f}")
        guidance = _REMEDIATION[code]
        alerts.append(
            {
                "code": code,
                "severity": guidance["urgency"],
                "previous": round(prev, 4),
                "current": round(curr, 4),
                "delta": round(curr - prev, 4),
                "playbook": guidance["playbook"],
                "suggested_actions": guidance["suggested_actions"],
            }
        )
    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"previous": prev, "current": curr, "alert_count": len(alerts)},
        "metadata": {"gate": "security_trend_gate"},
    }
    alert_report = {
        "status": "OK" if not alerts else "ALERT",
        "findings": [a["code"] for a in alerts],
        "summary": {"alerts": alerts, "total_alerts": len(alerts), "runbook_owner": "security-operations"},
        "metadata": {"gate": "security_trend_alert", "source_report": "security_trend_gate.json"},
    }
    out = sec / "security_trend_gate.json"
    alert_out = sec / "security_trend_alert.json"
    write_json_report(out, report)
    write_json_report(alert_out, alert_report)
    print(f"SECURITY_TREND_GATE: {report['status']}")
    print(f"Report: {out}")
    print(f"Alert: {alert_out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
