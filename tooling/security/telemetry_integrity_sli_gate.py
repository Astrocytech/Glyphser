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
POLICY = ROOT / "governance" / "security" / "security_observability_policy.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = _load_json(POLICY)
    telemetry = policy.get("telemetry_integrity", {})
    if not isinstance(telemetry, dict):
        telemetry = {}

    report_glob = str(telemetry.get("report_glob", "*.json")).strip() or "*.json"
    excludes_raw = telemetry.get(
        "exclude_reports",
        ["telemetry_integrity_sli_gate.json", "telemetry_integrity_trend_alert.json", "telemetry_integrity_sli_history.json"],
    )
    excludes = {str(x).strip() for x in excludes_raw if isinstance(x, str) and str(x).strip()}
    threshold = float(telemetry.get("signed_reports_ratio_threshold", 0.0))
    history_window_runs = int(telemetry.get("history_window_runs", 30))
    drop_alert_threshold = float(telemetry.get("ratio_drop_alert_threshold", 0.05))

    sec = evidence_root() / "security"
    findings: list[str] = []
    reports = [p for p in sorted(sec.glob(report_glob)) if p.name not in excludes and p.suffix == ".json"]

    signed = 0
    unsigned_reports: list[str] = []
    for report in reports:
        sig_path = report.with_suffix(report.suffix + ".sig")
        if sig_path.exists():
            signed += 1
        else:
            unsigned_reports.append(report.name)

    total = len(reports)
    ratio = (signed / total) if total else 1.0
    if ratio < threshold:
        findings.append(f"telemetry_integrity_below_threshold:{ratio:.4f}<{threshold:.4f}")

    history_path = sec / "telemetry_integrity_sli_history.json"
    history_payload: dict[str, Any] = {}
    if history_path.exists():
        try:
            history_payload = _load_json(history_path)
        except Exception:
            history_payload = {}

    values_raw = history_payload.get("values", []) if isinstance(history_payload, dict) else []
    values = [float(v) for v in values_raw if isinstance(v, (int, float))]
    previous_ratio = values[-1] if values else None
    values.append(ratio)
    if history_window_runs > 0:
        values = values[-history_window_runs:]

    _write_json(history_path, {"values": values, "window": history_window_runs})

    alerts: list[dict[str, Any]] = []
    if previous_ratio is not None and ratio + drop_alert_threshold < previous_ratio:
        alerts.append(
            {
                "code": "telemetry_integrity_ratio_drop",
                "previous_ratio": previous_ratio,
                "current_ratio": ratio,
                "drop": previous_ratio - ratio,
                "drop_alert_threshold": drop_alert_threshold,
            }
        )

    alert_report = {
        "status": "ALERT" if alerts else "PASS",
        "findings": [item["code"] for item in alerts],
        "summary": {
            "alerts": alerts,
            "current_ratio": ratio,
            "previous_ratio": previous_ratio,
        },
        "metadata": {"gate": "telemetry_integrity_trend_alert"},
    }
    alert_out = sec / "telemetry_integrity_trend_alert.json"
    write_json_report(alert_out, alert_report)

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "reports_scanned": total,
            "signed_reports": signed,
            "unsigned_reports": unsigned_reports,
            "signed_reports_ratio": ratio,
            "signed_reports_ratio_threshold": threshold,
            "history_window_runs": history_window_runs,
            "ratio_drop_alert_threshold": drop_alert_threshold,
        },
        "metadata": {"gate": "telemetry_integrity_sli_gate"},
    }
    out = sec / "telemetry_integrity_sli_gate.json"
    write_json_report(out, report)
    print(f"TELEMETRY_INTEGRITY_SLI_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
