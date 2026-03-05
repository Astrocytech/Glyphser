#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import sys
from datetime import UTC, datetime
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


def _parse_utc(value: str) -> datetime | None:
    raw = value.strip()
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = f"{raw[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None
    return parsed.astimezone(UTC) if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def _reference_now() -> datetime:
    fixed = _parse_utc(str(os.environ.get("GLYPHSER_FIXED_UTC", "")))
    return fixed or datetime.now(UTC)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = _load_json(POLICY)
    telemetry = policy.get("telemetry_timeliness", {})
    if not isinstance(telemetry, dict):
        telemetry = {}

    required_raw = telemetry.get(
        "required_reports",
        [
            "security_event_export.json",
            "security_event_schema_gate.json",
            "telemetry_completeness_sli_gate.json",
        ],
    )
    required_reports = [
        str(item).strip() for item in required_raw if isinstance(item, str) and str(item).strip()
    ]
    max_age_minutes = float(telemetry.get("max_report_age_minutes", 30.0))
    threshold = float(telemetry.get("timely_reports_rate_threshold", 1.0))
    allowed_future_skew_minutes = float(telemetry.get("allowed_future_skew_minutes", 2.0))

    sec = evidence_root() / "security"
    findings: list[str] = []
    ages: dict[str, float] = {}
    timely = 0
    checked = 0
    now = _reference_now()

    for name in required_reports:
        checked += 1
        path = sec / name
        if not path.exists():
            findings.append(f"missing_required_report:{name}")
            continue
        try:
            payload = _load_json(path)
        except Exception:
            findings.append(f"invalid_json_report:{name}")
            continue
        metadata = payload.get("metadata", {})
        if not isinstance(metadata, dict):
            findings.append(f"missing_metadata:{name}")
            continue
        generated_at = _parse_utc(str(metadata.get("generated_at_utc", "")))
        if generated_at is None:
            findings.append(f"missing_generated_at_utc:{name}")
            continue
        age_minutes = (now - generated_at).total_seconds() / 60.0
        ages[name] = age_minutes

        if age_minutes < -allowed_future_skew_minutes:
            findings.append(
                f"report_generated_in_future:{name}:{age_minutes:.2f}<-{allowed_future_skew_minutes:.2f}"
            )
            continue
        if age_minutes > max_age_minutes:
            findings.append(f"report_stale:{name}:{age_minutes:.2f}>{max_age_minutes:.2f}")
            continue
        timely += 1

    rate = (timely / checked) if checked else 1.0
    if rate < threshold:
        findings.append(f"telemetry_timeliness_below_threshold:{rate:.4f}<{threshold:.4f}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "required_reports": required_reports,
            "reports_checked": checked,
            "timely_reports": timely,
            "timely_reports_rate": rate,
            "timely_reports_rate_threshold": threshold,
            "max_report_age_minutes": max_age_minutes,
            "allowed_future_skew_minutes": allowed_future_skew_minutes,
            "report_age_minutes": ages,
        },
        "metadata": {"gate": "telemetry_timeliness_sli_gate", "reference_time_utc": now.isoformat()},
    }
    out = sec / "telemetry_timeliness_sli_gate.json"
    write_json_report(out, report)
    print(f"TELEMETRY_TIMELINESS_SLI_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
