#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

PERSISTENT_HISTORY = ROOT / "evidence" / "security" / "ci_failure_classifier_history.json"
OWNER_MAP_PATH = ROOT / "governance" / "security" / "ci_failure_owner_map.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _parse_ts(text: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(str(text).replace("Z", "+00:00"))
    except Exception:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def _issue_first_seen(runs: list[dict[str, Any]]) -> dict[str, datetime]:
    out: dict[str, datetime] = {}
    for run in runs:
        ts = _parse_ts(run.get("timestamp_utc", ""))
        issues = run.get("issues", [])
        if ts is None or not isinstance(issues, list):
            continue
        for issue in issues:
            if not isinstance(issue, str) or not issue.strip():
                continue
            existing = out.get(issue)
            if existing is None or ts < existing:
                out[issue] = ts
    return out


def _monthly_frequency(runs: list[dict[str, Any]], year: int, month: int) -> dict[str, int]:
    freq: dict[str, int] = {}
    for run in runs:
        ts = _parse_ts(run.get("timestamp_utc", ""))
        issues = run.get("issues", [])
        if ts is None or ts.year != year or ts.month != month or not isinstance(issues, list):
            continue
        for issue in sorted({str(item).strip() for item in issues if isinstance(item, str) and str(item).strip()}):
            freq[issue] = freq.get(issue, 0) + 1
    return freq


def _owner_config(findings: list[str]) -> dict[str, Any]:
    if not OWNER_MAP_PATH.exists():
        findings.append("missing_ci_failure_owner_map")
        return {}
    try:
        return _load_json(OWNER_MAP_PATH)
    except Exception:
        findings.append("invalid_ci_failure_owner_map")
        return {}


def _owner_for_issue(issue: str, config: dict[str, Any]) -> tuple[str, str, int]:
    default_owner = str(config.get("default_owner", "security-team")).strip() or "security-team"
    default_eta_days_raw = config.get("default_eta_days", 30)
    try:
        default_eta_days = int(default_eta_days_raw)
    except Exception:
        default_eta_days = 30
    if default_eta_days <= 0:
        default_eta_days = 30

    by_issue = config.get("issue_overrides", {}) if isinstance(config, dict) else {}
    by_report = config.get("report_owner_overrides", {}) if isinstance(config, dict) else {}
    issue_cfg = by_issue.get(issue, {}) if isinstance(by_issue, dict) else {}

    report_name = issue.split(":", 1)[0] if ":" in issue else issue
    report_cfg = by_report.get(report_name, {}) if isinstance(by_report, dict) else {}

    owner = str(issue_cfg.get("owner") or report_cfg.get("owner") or default_owner).strip() or default_owner
    action = str(
        issue_cfg.get("action")
        or report_cfg.get("action")
        or f"Investigate and remediate recurring issue in {report_name}."
    ).strip()
    eta_days_raw = issue_cfg.get("eta_days", report_cfg.get("eta_days", default_eta_days))
    try:
        eta_days = int(eta_days_raw)
    except Exception:
        eta_days = default_eta_days
    if eta_days <= 0:
        eta_days = default_eta_days
    return owner, action, eta_days


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not PERSISTENT_HISTORY.exists():
        findings.append("missing_ci_failure_classifier_history")
        history = {}
    else:
        try:
            history = _load_json(PERSISTENT_HISTORY)
        except Exception:
            findings.append("invalid_ci_failure_classifier_history")
            history = {}

    counts_raw = history.get("counts", {}) if isinstance(history, dict) else {}
    counts: dict[str, int] = {}
    if isinstance(counts_raw, dict):
        for key, value in counts_raw.items():
            if not isinstance(key, str):
                continue
            try:
                score = int(value)
            except Exception:
                continue
            if score > 0:
                counts[key] = score

    runs_raw = history.get("runs", []) if isinstance(history, dict) else []
    runs = [item for item in runs_raw if isinstance(item, dict)] if isinstance(runs_raw, list) else []

    now = datetime.now(UTC)
    monthly_counts = _monthly_frequency(runs, now.year, now.month)
    first_seen = _issue_first_seen(runs)
    config = _owner_config(findings)

    recurring = [issue for issue, count in counts.items() if count >= 2]
    ranked = sorted(recurring, key=lambda issue: (-monthly_counts.get(issue, 0), -counts[issue], issue))

    top_items: list[dict[str, Any]] = []
    for issue in ranked[:10]:
        owner, action, eta_days = _owner_for_issue(issue, config)
        first = first_seen.get(issue)
        eta = (first or now) + timedelta(days=eta_days)
        top_items.append(
            {
                "issue": issue,
                "owner": owner,
                "action": action,
                "action_eta_utc": eta.isoformat(),
                "total_occurrences": counts[issue],
                "monthly_occurrences": monthly_counts.get(issue, 0),
                "first_seen_utc": first.isoformat() if first else "",
            }
        )

    report = {
        "status": "PASS" if not top_items and not findings else "WARN",
        "findings": findings,
        "summary": {
            "month": f"{now.year:04d}-{now.month:02d}",
            "ranked_recurring_issues": len(top_items),
            "total_recurring_issues": len(recurring),
            "owner_map_path": str(OWNER_MAP_PATH.relative_to(ROOT)).replace("\\", "/"),
            "history_path": str(PERSISTENT_HISTORY.relative_to(ROOT)).replace("\\", "/"),
        },
        "top_recurring_failures": top_items,
        "metadata": {"gate": "monthly_top_recurring_failures_report"},
    }
    out = evidence_root() / "security" / "monthly_top_recurring_failures_report.json"
    write_json_report(out, report)
    print(f"MONTHLY_TOP_RECURRING_FAILURES_REPORT: {report['status']}")
    print(f"Report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
