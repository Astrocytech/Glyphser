#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from tooling.lib.path_config import evidence_root

ROOT = Path(__file__).resolve().parents[2]
METADATA_DIR = ROOT / "governance" / "security" / "metadata"
DEFAULT_MAX_REVIEW_AGE_DAYS = 180


def _now_utc() -> datetime:
    sde = os.environ.get("SOURCE_DATE_EPOCH", "").strip()
    if sde:
        try:
            return datetime.fromtimestamp(int(sde), tz=UTC)
        except (ValueError, OSError):
            ...
    fixed = os.environ.get("GLYPHSER_FIXED_UTC", "").strip()
    if fixed:
        try:
            return datetime.fromisoformat(fixed)
        except ValueError:
            ...
    return datetime.now(UTC)


def _parse_iso(ts: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(ts)
    except Exception:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    checked = 0
    now = _now_utc()

    for path in sorted(METADATA_DIR.glob("*.meta.json")):
        checked += 1
        payload: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            findings.append(f"invalid_metadata_object:{path.name}")
            continue
        policy_version = payload.get("policy_version")
        reviewed_raw = str(payload.get("last_reviewed_utc", "")).strip()
        if not reviewed_raw:
            findings.append(f"missing_last_reviewed_utc:{path.name}")
            continue
        reviewed_at = _parse_iso(reviewed_raw)
        if reviewed_at is None:
            findings.append(f"invalid_last_reviewed_utc:{path.name}")
            continue
        if not isinstance(policy_version, str) or not policy_version.strip():
            findings.append(f"missing_policy_version:{path.name}")

        max_age = int(payload.get("max_review_age_days", DEFAULT_MAX_REVIEW_AGE_DAYS))
        age = now - reviewed_at
        if age > timedelta(days=max_age):
            findings.append(f"stale_review:{path.name}:age_days={age.days}:max_days={max_age}")

    if checked == 0:
        findings.append("missing_policy_metadata_files")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "checked_metadata_files": checked,
            "default_max_review_age_days": DEFAULT_MAX_REVIEW_AGE_DAYS,
            "now_utc": now.isoformat(),
        },
        "metadata": {"gate": "stale_policy_review_gate"},
    }
    out = evidence_root() / "security" / "stale_policy_review_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"STALE_POLICY_REVIEW_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
