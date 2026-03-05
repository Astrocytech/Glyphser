#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

HISTORY_PATH = ROOT / "evidence" / "security" / "ci_failure_classifier_history.json"
CLOSURE_REQUESTS = ROOT / "governance" / "security" / "ci_failure_closure_requests.json"
CHRONIC_THRESHOLD = 5


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _parse_ts(text: str) -> datetime:
    return datetime.fromisoformat(str(text).replace("Z", "+00:00"))


def _sorted_runs(history: dict[str, Any]) -> list[dict[str, Any]]:
    raw = history.get("runs", []) if isinstance(history, dict) else []
    runs = [item for item in raw if isinstance(item, dict)] if isinstance(raw, list) else []

    def _key(item: dict[str, Any]) -> tuple[int, str]:
        try:
            ts = _parse_ts(str(item.get("timestamp_utc", "")))
            return (0, ts.isoformat())
        except Exception:
            return (1, str(item.get("timestamp_utc", "")))

    return sorted(runs, key=_key)


def _issues(run: dict[str, Any]) -> set[str]:
    raw = run.get("issues", [])
    if not isinstance(raw, list):
        return set()
    return {str(item).strip() for item in raw if isinstance(item, str) and str(item).strip()}


def _consecutive_green_runs(runs: list[dict[str, Any]], issue: str) -> int:
    clean = 0
    for run in reversed(runs):
        if issue in _issues(run):
            break
        clean += 1
    return clean


def _normalized_counts(history: dict[str, Any]) -> dict[str, int]:
    raw = history.get("counts", {}) if isinstance(history, dict) else {}
    if not isinstance(raw, dict):
        return {}
    out: dict[str, int] = {}
    for key, value in raw.items():
        if not isinstance(key, str):
            continue
        try:
            count = int(value)
        except Exception:
            continue
        if count > 0:
            out[key] = count
    return out


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not HISTORY_PATH.exists():
        findings.append("missing_ci_failure_classifier_history")
        history = {}
    else:
        try:
            history = _load_json(HISTORY_PATH)
        except Exception:
            history = {}
            findings.append("invalid_ci_failure_classifier_history")

    if not CLOSURE_REQUESTS.exists():
        findings.append("missing_ci_failure_closure_requests")
        requests_payload = {}
    else:
        try:
            requests_payload = _load_json(CLOSURE_REQUESTS)
        except Exception:
            requests_payload = {}
            findings.append("invalid_ci_failure_closure_requests")

    required_green_runs = 3
    try:
        candidate = int(requests_payload.get("required_green_runs", required_green_runs))
        if candidate > 0:
            required_green_runs = candidate
    except Exception:
        pass

    requested = requests_payload.get("requested_resolutions", []) if isinstance(requests_payload, dict) else []
    requested_issues = sorted({str(item).strip() for item in requested if isinstance(item, str) and str(item).strip()})

    runs = _sorted_runs(history)
    latest_issues = _issues(runs[-1]) if runs else set()
    chronic_active_issues = sorted(
        issue
        for issue, count in _normalized_counts(history).items()
        if count >= CHRONIC_THRESHOLD and issue in latest_issues
    )

    requested_issue_set = set(requested_issues)
    for issue in chronic_active_issues:
        if issue not in requested_issue_set:
            findings.append(f"chronic_issue_missing_closure_request:{issue}")

    verified: list[str] = []
    pending: list[dict[str, Any]] = []

    for issue in requested_issues:
        clean_runs = _consecutive_green_runs(runs, issue)
        if clean_runs >= required_green_runs:
            verified.append(issue)
            continue
        pending.append({"issue": issue, "clean_runs": clean_runs, "required_green_runs": required_green_runs})
        findings.append(
            f"closure_insufficient_green_runs:{issue}:clean_runs:{clean_runs}:required:{required_green_runs}"
        )

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "required_green_runs": required_green_runs,
            "requested_resolutions": len(requested_issues),
            "verified_resolutions": len(verified),
            "pending_resolutions": len(pending),
            "chronic_active_issue_count": len(chronic_active_issues),
            "history_path": str(HISTORY_PATH.relative_to(ROOT)).replace("\\", "/"),
            "closure_requests_path": str(CLOSURE_REQUESTS.relative_to(ROOT)).replace("\\", "/"),
        },
        "verification": {
            "verified": verified,
            "pending": pending,
            "chronic_active_issues": chronic_active_issues,
        },
        "metadata": {"gate": "recurring_failure_closure_gate"},
    }
    out = evidence_root() / "security" / "recurring_failure_closure_gate.json"
    write_json_report(out, report)
    print(f"RECURRING_FAILURE_CLOSURE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
