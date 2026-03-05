#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

TODO = ROOT / "glyphser_security_hardening_master_todo.txt"
REGISTRY = ROOT / "governance" / "security" / "hardening_pending_item_registry.json"
PERSISTENT_HISTORY = ROOT / "evidence" / "security" / "hardening_completion_metrics_history.json"
EXCLUDED_STATUS_REPORTS = {
    "hardening_completion_metrics.json",
    "hardening_completion_metrics_history.json",
}


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _pending_count() -> int:
    if not TODO.exists():
        return 0
    total = 0
    for raw in TODO.read_text(encoding="utf-8").splitlines():
        if raw.strip().startswith("[ ]"):
            total += 1
    return total


def _today_utc() -> str:
    return datetime.now(UTC).date().isoformat()


def _done_count() -> int:
    if not REGISTRY.exists():
        return 0
    try:
        payload = _load_json(REGISTRY)
    except Exception:
        return 0
    entries = payload.get("entries", []) if isinstance(payload.get("entries", []), list) else []
    total = 0
    for row in entries:
        if not isinstance(row, dict):
            continue
        if str(row.get("status", "")).strip().lower() == "done":
            total += 1
    return total


def _regression_reopen_total() -> int:
    if not REGISTRY.exists():
        return 0
    try:
        payload = _load_json(REGISTRY)
    except Exception:
        return 0
    entries = payload.get("entries", []) if isinstance(payload.get("entries", []), list) else []
    total = 0
    for row in entries:
        if not isinstance(row, dict):
            continue
        if str(row.get("reopen_reason", "")).strip().lower() == "regression_detected":
            total += 1
    return total


def _hardening_throughput(daily: list[dict[str, Any]], today_done_count: int, date_key: str) -> int:
    if not daily:
        return 0
    previous_done_count = 0
    lookback = sorted(
        [row for row in daily if str(row.get("date", "")).strip() < date_key],
        key=lambda row: str(row.get("date", "")),
    )
    if lookback:
        previous_done_count = int(lookback[max(0, len(lookback) - 7)].get("done_count", 0))
    return max(0, today_done_count - previous_done_count)


def _weekly_delta(daily: list[dict[str, Any]], date_key: str, field: str, current_value: int) -> int:
    previous_value = 0
    lookback = sorted(
        [row for row in daily if str(row.get("date", "")).strip() < date_key],
        key=lambda row: str(row.get("date", "")),
    )
    if lookback:
        previous_value = int(lookback[max(0, len(lookback) - 7)].get(field, 0))
    return max(0, current_value - previous_value)


def _ci_security_green(sec: Path) -> bool:
    reports = sorted(path for path in sec.glob("*.json") if path.name not in EXCLUDED_STATUS_REPORTS)
    saw_status = False
    for path in reports:
        try:
            payload = _load_json(path)
        except Exception:
            return False
        status = str(payload.get("status", "")).strip().upper()
        if not status:
            continue
        saw_status = True
        if status != "PASS":
            return False
    return saw_status


def _updated_runs(payload: dict[str, Any], current_run: dict[str, Any]) -> list[dict[str, Any]]:
    raw = payload.get("runs", [])
    runs = [item for item in raw if isinstance(item, dict)] if isinstance(raw, list) else []
    runs.append(current_run)
    return runs[-200:]


def _ci_security_green_streak(runs: list[dict[str, Any]]) -> int:
    streak = 0
    for row in reversed(runs):
        if bool(row.get("ci_security_green")):
            streak += 1
        else:
            break
    return streak


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    if not TODO.exists():
        findings.append("missing_hardening_todo")

    pending_item_count = _pending_count()
    done_count = _done_count()
    regression_reopen_total = _regression_reopen_total()
    date_key = _today_utc()

    history_payload: dict[str, Any] = {}
    if PERSISTENT_HISTORY.exists():
        try:
            history_payload = _load_json(PERSISTENT_HISTORY)
        except Exception:
            findings.append("invalid_hardening_completion_metrics_history")
            history_payload = {}

    daily_raw = history_payload.get("daily", []) if isinstance(history_payload.get("daily", []), list) else []
    daily = [item for item in daily_raw if isinstance(item, dict)]

    updated = False
    for row in daily:
        if str(row.get("date", "")).strip() == date_key:
            row["pending_item_count"] = pending_item_count
            row["done_count"] = done_count
            row["regression_reopen_total"] = regression_reopen_total
            updated = True
            break
    if not updated:
        daily.append(
            {
                "date": date_key,
                "pending_item_count": pending_item_count,
                "done_count": done_count,
                "regression_reopen_total": regression_reopen_total,
            }
        )

    hardening_throughput = _hardening_throughput(daily, done_count, date_key)
    regression_reopens_weekly = _weekly_delta(daily, date_key, "regression_reopen_total", regression_reopen_total)
    regression_reopen_rate = (
        float(regression_reopens_weekly) / float(hardening_throughput) if hardening_throughput > 0 else 0.0
    )

    sec = evidence_root() / "security"
    ci_security_green = _ci_security_green(sec) if sec.exists() else False
    current_run = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "date": date_key,
        "ci_security_green": ci_security_green,
    }
    runs = _updated_runs(history_payload, current_run)
    ci_security_green_streak = _ci_security_green_streak(runs)

    history = {
        "schema_version": 1,
        "updated_at_utc": datetime.now(UTC).isoformat(),
        "daily": sorted(daily, key=lambda row: str(row.get("date", ""))),
        "runs": runs,
    }
    _write_json(PERSISTENT_HISTORY, history)

    _write_json(sec / "hardening_completion_metrics_history.json", history)

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "date": date_key,
            "pending_item_count": pending_item_count,
            "done_count": done_count,
            "hardening_throughput": hardening_throughput,
            "regression_reopens_weekly": regression_reopens_weekly,
            "regression_reopen_rate": regression_reopen_rate,
            "ci_security_green_streak": ci_security_green_streak,
            "history_days": len(history["daily"]),
            "history_runs": len(history["runs"]),
        },
        "metrics": {
            "pending_item_count": {
                "date": date_key,
                "value": pending_item_count,
                "unit": "items",
                "cadence": "daily",
            },
            "hardening_throughput": {
                "date": date_key,
                "value": hardening_throughput,
                "unit": "items_closed_per_week",
                "cadence": "weekly",
            },
            "regression_reopen_rate": {
                "date": date_key,
                "value": regression_reopen_rate,
                "unit": "reopened_per_closed_item",
                "cadence": "weekly",
            },
            "ci_security_green_streak": {
                "date": date_key,
                "value": ci_security_green_streak,
                "unit": "consecutive_green_runs",
                "cadence": "per_run",
            },
        },
        "metadata": {"report": "hardening_completion_metrics"},
    }
    out = sec / "hardening_completion_metrics.json"
    write_json_report(out, report)
    print(f"HARDENING_COMPLETION_METRICS: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
