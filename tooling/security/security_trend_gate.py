#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from datetime import UTC, datetime
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


def _load_policy() -> dict[str, object]:
    path = ROOT / "governance" / "security" / "security_observability_policy.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _as_dict(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def _can_emit_alert(run_index: int, last_at: int, suppress_at: int, dedup_window: int) -> bool:
    if run_index <= suppress_at:
        return False
    if last_at <= 0:
        return True
    if dedup_window <= 0:
        return True
    return run_index - last_at > dedup_window


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    policy = _load_policy()
    history_window = int(policy.get("history_window_runs", 30))
    if history_window < 5:
        history_window = 30
    noise = _as_dict(policy.get("noise_control"))
    dedup_window = int(noise.get("dedup_window_runs", 2))
    suppression_ttl = int(noise.get("suppression_ttl_runs", 3))
    if dedup_window < 0:
        dedup_window = 0
    if suppression_ttl < 0:
        suppression_ttl = 0
    burn_rate_threshold = float(policy.get("burn_rate_alert_threshold", 2.0))
    if burn_rate_threshold < 0.0:
        burn_rate_threshold = 2.0
    silent = _as_dict(policy.get("silent_failure_detection"))
    max_report_age_hours = int(silent.get("max_report_age_hours", 26))
    required_reports = [
        str(x)
        for x in silent.get(
            "required_security_reports",
            ["security_slo_report.json", "security_super_gate.json", "policy_signature.json", "provenance_signature.json"],
        )
        if isinstance(x, str) and x.strip()
    ]
    state_path = sec / "security_trend_alert_state.json"
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
    if not isinstance(state, dict):
        state = {}
    last_seen = state.get("last_seen", {})
    suppressed_until = state.get("suppressed_until", {})
    if not isinstance(last_seen, dict):
        last_seen = {}
    if not isinstance(suppressed_until, dict):
        suppressed_until = {}

    current_path = sec / "security_slo_report.json"
    hist_path = sec / "security_slo_history.json"
    current = json.loads(current_path.read_text(encoding="utf-8")) if current_path.exists() else {}
    if not isinstance(current, dict):
        current = {}
    history = json.loads(hist_path.read_text(encoding="utf-8")) if hist_path.exists() else {"values": []}
    values = history.get("values", []) if isinstance(history, dict) else []
    if not isinstance(values, list):
        values = []
    curr = float(current.get("summary", {}).get("pass_rate", 0.0)) if isinstance(current, dict) else 0.0
    prev = float(values[-1]) if values else curr
    run_index = len(values) + 1
    values.append(curr)
    history = {"values": values[-history_window:]}
    hist_path.write_text(json.dumps(history, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    findings: list[str] = []
    alerts: list[dict[str, object]] = []
    now = datetime.now(UTC)
    for report_name in required_reports:
        path = sec / report_name
        if not path.exists():
            findings.append(f"security_silent_failure_missing_output:{report_name}")
            continue
        age_hours = int((now.timestamp() - path.stat().st_mtime) // 3600)
        if age_hours > max_report_age_hours:
            findings.append(f"security_silent_failure_stale_output:{report_name}:{age_hours}h")
    required_slo_fields = {"status", "findings", "summary", "metadata"}
    if current and not required_slo_fields.issubset(set(current.keys())):
        findings.append("security_silent_failure_partial_output:security_slo_report.json")

    if curr + 0.05 < prev:
        code = "security_trend_degrading"
        findings.append(f"{code}:{prev:.3f}->{curr:.3f}")
        guidance = _REMEDIATION[code]
        suppress_at = int(suppressed_until.get(code, 0))
        last_at = int(last_seen.get(code, 0))
        if _can_emit_alert(run_index, last_at, suppress_at, dedup_window):
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
            last_seen[code] = run_index
            suppressed_until[code] = run_index + suppression_ttl
    burn_rate = float(current.get("summary", {}).get("burn_rate", 0.0)) if isinstance(current, dict) else 0.0
    if burn_rate > burn_rate_threshold:
        findings.append(f"security_slo_burn_rate_above_threshold:{burn_rate:.3f}")
        code = "security_slo_burn_rate_alert"
        suppress_at = int(suppressed_until.get(code, 0))
        last_at = int(last_seen.get(code, 0))
        if _can_emit_alert(run_index, last_at, suppress_at, dedup_window):
            alerts.append(
                {
                    "code": code,
                    "severity": "high",
                    "burn_rate": round(burn_rate, 4),
                    "threshold": burn_rate_threshold,
                    "playbook": "governance/security/INCIDENT_RUNBOOKS.md",
                    "suggested_actions": [
                        "Stabilize failing controls and recover security pass rate.",
                        "Escalate to incident workflow if burn rate remains above threshold.",
                    ],
                }
            )
            last_seen[code] = run_index
            suppressed_until[code] = run_index + suppression_ttl
    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "previous": prev,
            "current": curr,
            "burn_rate": burn_rate,
            "burn_rate_threshold": burn_rate_threshold,
            "alert_count": len(alerts),
            "dedup_window_runs": dedup_window,
            "suppression_ttl_runs": suppression_ttl,
        },
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
    write_json_report(
        state_path,
        {"last_seen": last_seen, "suppressed_until": suppressed_until, "run_index": run_index},
    )
    write_json_report(out, report)
    write_json_report(alert_out, alert_report)
    print(f"SECURITY_TREND_GATE: {report['status']}")
    print(f"Report: {out}")
    print(f"Alert: {alert_out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
