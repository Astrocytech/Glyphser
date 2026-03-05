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

REVIEW = ROOT / "governance" / "security" / "security_optimization_review.json"
MAX_REVIEW_AGE_DAYS = 90


def _now_utc() -> datetime:
    fixed = os.environ.get("GLYPHSER_FIXED_UTC", "").strip()
    if fixed:
        return datetime.fromisoformat(fixed)
    return datetime.now(UTC)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not REVIEW.exists():
        findings.append("missing_optimization_review_record")
        payload: dict[str, Any] = {}
    else:
        try:
            payload = _load_json(REVIEW)
        except Exception:
            payload = {}
            findings.append("invalid_optimization_review_record")

    reviewed_at = str(payload.get("reviewed_at_utc", ""))
    affirmed = bool(payload.get("affirmed_no_security_semantics_change", False))
    if not affirmed:
        findings.append("optimization_review_missing_semantic_safety_affirmation")

    age_days: float | None = None
    if reviewed_at:
        try:
            reviewed_dt = datetime.fromisoformat(reviewed_at)
            age_days = (_now_utc() - reviewed_dt).total_seconds() / 86400.0
            if age_days > MAX_REVIEW_AGE_DAYS:
                findings.append(f"optimization_review_stale:{age_days:.1f}d>{MAX_REVIEW_AGE_DAYS}d")
        except ValueError:
            findings.append("invalid_reviewed_at_utc")
    else:
        findings.append("missing_reviewed_at_utc")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "review_record": str(REVIEW.relative_to(ROOT)).replace("\\", "/"),
            "max_review_age_days": MAX_REVIEW_AGE_DAYS,
            "review_age_days": round(age_days, 3) if age_days is not None else None,
        },
        "metadata": {"gate": "security_optimization_review_gate"},
    }
    out = evidence_root() / "security" / "security_optimization_review_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_OPTIMIZATION_REVIEW_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
