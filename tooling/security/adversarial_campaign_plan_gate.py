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

PLAN_PATH = ROOT / "governance" / "security" / "adversarial_campaign_plan.json"


def _parse_ts(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=UTC)


def _now_utc() -> datetime:
    fixed = os.environ.get("GLYPHSER_FIXED_UTC", "").strip()
    parsed = _parse_ts(fixed) if fixed else None
    return parsed or datetime.now(UTC)


def _load_plan(path: Path) -> tuple[list[dict[str, Any]], str]:
    if not path.exists():
        return [], "missing_adversarial_campaign_plan"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return [], "invalid_adversarial_campaign_plan_json"
    if not isinstance(payload, dict):
        return [], "invalid_adversarial_campaign_plan_schema"
    campaigns = payload.get("campaigns", [])
    if not isinstance(campaigns, list):
        return [], "invalid_adversarial_campaign_list"
    return [item for item in campaigns if isinstance(item, dict)], ""


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    now = _now_utc()
    campaigns, load_error = _load_plan(PLAN_PATH)
    if load_error:
        findings.append(load_error)

    parsed_campaigns: list[tuple[dict[str, Any], datetime]] = []
    for idx, campaign in enumerate(campaigns):
        campaign_id = str(campaign.get("campaign_id", "")).strip()
        planned_at = _parse_ts(campaign.get("planned_at_utc"))
        if not campaign_id:
            findings.append(f"missing_campaign_id:{idx}")
            continue
        if planned_at is None:
            findings.append(f"missing_or_invalid_planned_at_utc:{campaign_id}")
            continue

        matrix = campaign.get("scenario_coverage_matrix", [])
        outcomes = campaign.get("signed_outcomes", [])
        if not isinstance(matrix, list) or not matrix:
            findings.append(f"missing_scenario_coverage_matrix:{campaign_id}")
        else:
            for row in matrix:
                if not isinstance(row, dict):
                    findings.append(f"invalid_coverage_matrix_row:{campaign_id}")
                    continue
                if not str(row.get("scenario_id", "")).strip():
                    findings.append(f"missing_scenario_id:{campaign_id}")
                if not str(row.get("coverage_status", "")).strip():
                    findings.append(f"missing_coverage_status:{campaign_id}")

        if not isinstance(outcomes, list) or not outcomes:
            findings.append(f"missing_signed_outcomes:{campaign_id}")
        else:
            for row in outcomes:
                if not isinstance(row, dict):
                    findings.append(f"invalid_signed_outcome:{campaign_id}")
                    continue
                outcome_id = str(row.get("outcome_id", "")).strip()
                executed_at = _parse_ts(row.get("executed_at_utc"))
                signature = str(row.get("outcome_signature", "")).strip()
                if not outcome_id:
                    findings.append(f"missing_outcome_id:{campaign_id}")
                if executed_at is None:
                    findings.append(f"missing_or_invalid_executed_at_utc:{campaign_id}")
                if not signature:
                    findings.append(f"missing_outcome_signature:{campaign_id}")

        parsed_campaigns.append((campaign, planned_at))

    latest = max((item[1] for item in parsed_campaigns), default=None)
    days_since_latest = int((now - latest).total_seconds() // 86400) if latest else None
    if latest is None:
        findings.append("no_campaigns_defined")
    elif days_since_latest is not None and days_since_latest > 92:
        findings.append(f"adversarial_campaign_plan_stale:{days_since_latest}d")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "plan_path": str(PLAN_PATH),
            "campaigns": len(campaigns),
            "latest_planned_at_utc": latest.isoformat() if latest else "",
            "days_since_latest_campaign": days_since_latest if days_since_latest is not None else -1,
        },
        "metadata": {"gate": "adversarial_campaign_plan_gate"},
    }
    out = evidence_root() / "security" / "adversarial_campaign_plan_gate.json"
    write_json_report(out, report)
    print(f"ADVERSARIAL_CAMPAIGN_PLAN_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
