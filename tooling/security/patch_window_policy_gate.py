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

POLICY = ROOT / "governance" / "security" / "patch_window_policy.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _parse_utc(value: str) -> datetime | None:
    raw = value.strip()
    if not raw:
        return None
    candidate = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def _now_utc() -> datetime:
    fixed = os.environ.get("GLYPHSER_FIXED_UTC", "").strip()
    if fixed:
        parsed = _parse_utc(fixed)
        if parsed is not None:
            return parsed.astimezone(UTC)
    return datetime.now(UTC)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    checks: list[dict[str, Any]] = []

    if not POLICY.exists():
        findings.append("missing_patch_window_policy")
        policy: dict[str, Any] = {}
    else:
        policy = _load_json(POLICY)

    max_backfill_days = int(policy.get("max_backfill_days", 0) or 0)
    log_rel = str(policy.get("backfill_log_path", "")).strip()
    if max_backfill_days <= 0:
        findings.append("invalid_max_backfill_days")
    if not log_rel:
        findings.append("missing_backfill_log_path")
    log_path = ROOT / log_rel if log_rel else Path("")

    if log_rel and log_path.exists():
        log = _load_json(log_path)
        entries = log.get("entries", []) if isinstance(log, dict) else []
        if not isinstance(entries, list):
            entries = []
            findings.append("invalid_backfill_log_entries")
    else:
        entries = []
        if log_rel:
            findings.append("missing_backfill_log")

    now = _now_utc()
    for item in entries:
        if not isinstance(item, dict):
            findings.append("invalid_backfill_log_entry")
            continue
        fix_id = str(item.get("id", "")).strip() or "unknown_fix"
        applied_at = _parse_utc(str(item.get("applied_at_utc", "")).strip())
        if applied_at is None:
            findings.append(f"invalid_fix_applied_at:{fix_id}")
            continue

        tests_backfilled = bool(item.get("tests_backfilled", False))
        docs_backfilled = bool(item.get("docs_backfilled", False))
        backfilled_at = _parse_utc(str(item.get("backfilled_at_utc", "")).strip())
        age_days = (now - applied_at.astimezone(UTC)).total_seconds() / 86400.0
        within_window = age_days <= float(max_backfill_days)
        compliant = tests_backfilled and docs_backfilled and (backfilled_at is not None)

        checks.append(
            {
                "id": fix_id,
                "tests_backfilled": tests_backfilled,
                "docs_backfilled": docs_backfilled,
                "backfilled_at_present": backfilled_at is not None,
                "within_window": within_window,
            }
        )

        if not compliant and not within_window:
            findings.append(f"patch_window_backfill_overdue:{fix_id}")
        if compliant and backfilled_at is not None:
            backfill_age_days = (backfilled_at.astimezone(UTC) - applied_at.astimezone(UTC)).total_seconds() / 86400.0
            if backfill_age_days > float(max_backfill_days):
                findings.append(
                    f"patch_window_backfill_completed_outside_window:{fix_id}:{backfill_age_days:.2f}>{max_backfill_days}"
                )

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "max_backfill_days": max_backfill_days,
            "entries_checked": len(checks),
            "backfill_log_path": log_rel,
        },
        "metadata": {"gate": "patch_window_policy_gate"},
        "checks": checks,
    }

    out = evidence_root() / "security" / "patch_window_policy_gate.json"
    write_json_report(out, report)
    print(f"PATCH_WINDOW_POLICY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
