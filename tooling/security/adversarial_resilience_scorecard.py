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

HISTORY_PATH = ROOT / "governance" / "security" / "adversarial_detection_history.json"


def _now_utc() -> datetime:
    fixed = str(os.environ.get("GLYPHSER_FIXED_UTC", "")).strip()
    if fixed:
        try:
            parsed = datetime.fromisoformat(fixed.replace("Z", "+00:00"))
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
        except ValueError:
            pass
    return datetime.now(UTC)


def _load(path: Path) -> tuple[list[dict[str, Any]], str]:
    if not path.exists():
        return [], "missing_adversarial_detection_history"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return [], "invalid_adversarial_detection_history"
    rows = payload.get("events", []) if isinstance(payload, dict) else []
    if not isinstance(rows, list):
        return [], "invalid_adversarial_detection_history_schema"
    return [row for row in rows if isinstance(row, dict)], ""


def _num(value: object) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    events, load_err = _load(HISTORY_PATH)
    if load_err:
        findings.append(load_err)

    detection_latencies = [_num(event.get("detection_latency_minutes")) for event in events]
    containment_scores = [_num(event.get("containment_quality_score")) for event in events]
    event_count = len(events)
    mean_latency = round(sum(detection_latencies) / event_count, 3) if event_count else 0.0
    mean_containment = round(sum(containment_scores) / event_count, 3) if event_count else 0.0
    p95_latency = round(sorted(detection_latencies)[int(max(0, event_count - 1) * 0.95)], 3) if event_count else 0.0
    if event_count == 0:
        findings.append("no_adversarial_detection_events")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "scorecard_generated_at_utc": _now_utc().isoformat(),
            "history_path": str(HISTORY_PATH),
            "events": event_count,
            "mean_detection_latency_minutes": mean_latency,
            "p95_detection_latency_minutes": p95_latency,
            "mean_containment_quality_score": mean_containment,
        },
        "metadata": {"gate": "adversarial_resilience_scorecard"},
    }
    out = evidence_root() / "security" / "adversarial_resilience_scorecard.json"
    write_json_report(out, report)
    print(f"ADVERSARIAL_RESILIENCE_SCORECARD: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
