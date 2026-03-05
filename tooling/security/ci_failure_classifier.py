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

PERSISTENT_HISTORY = ROOT / "evidence" / "security" / "ci_failure_classifier_history.json"
HISTORY_SCHEMA_VERSION = 1
HISTORY_RUN_LIMIT = 200
EXCLUDED_REPORTS = {
    "ci_failure_classifier.json",
    "ci_failure_classifier_history.json",
    "ci_failure_classifier_persistent_history.json",
}


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _issue_keys(report_name: str, payload: dict[str, Any]) -> set[str]:
    status = str(payload.get("status", "")).strip().upper()
    if status not in {"FAIL", "WARN"}:
        return set()

    findings = payload.get("findings", [])
    if not isinstance(findings, list):
        findings = []

    keys: set[str] = set()
    for item in findings:
        if not isinstance(item, str):
            continue
        finding = item.strip()
        if finding:
            keys.add(f"{report_name}:{finding}")

    if not keys:
        keys.add(f"{report_name}:status:{status.lower()}")
    return keys


def _normalized_counts(payload: dict[str, Any]) -> dict[str, int]:
    raw = payload.get("counts", [])
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


def _updated_runs(payload: dict[str, Any], current_run: dict[str, Any]) -> list[dict[str, Any]]:
    raw = payload.get("runs", [])
    runs = [item for item in raw if isinstance(item, dict)] if isinstance(raw, list) else []
    runs.append(current_run)
    return runs[-HISTORY_RUN_LIMIT:]


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    findings: list[str] = []

    current_issues: set[str] = set()
    scanned_reports = 0
    if not sec.exists():
        findings.append("missing_security_evidence_directory")
    else:
        for path in sorted(sec.glob("*.json")):
            if path.name in EXCLUDED_REPORTS:
                continue
            try:
                payload = _load_json(path)
            except Exception:
                findings.append(f"invalid_security_report_json:{path.name}")
                continue
            scanned_reports += 1
            current_issues.update(_issue_keys(path.name, payload))

    history_payload: dict[str, Any] = {}
    if PERSISTENT_HISTORY.exists():
        try:
            history_payload = _load_json(PERSISTENT_HISTORY)
        except Exception:
            findings.append("invalid_persistent_history")
            history_payload = {}

    previous_counts = _normalized_counts(history_payload)
    updated_counts = dict(previous_counts)
    for issue in current_issues:
        updated_counts[issue] = updated_counts.get(issue, 0) + 1

    recurring_issues = sorted(issue for issue in current_issues if updated_counts.get(issue, 0) >= 2)
    chronic_issues = sorted(issue for issue in current_issues if updated_counts.get(issue, 0) >= 5)
    new_issues = sorted(issue for issue in current_issues if issue not in previous_counts)
    resolved_since_last = sorted(issue for issue in previous_counts if issue not in current_issues)

    top_recurring = [
        {"issue": key, "count": count}
        for key, count in sorted(updated_counts.items(), key=lambda item: (-item[1], item[0]))
        if count >= 2
    ][:10]

    run_id = str(os.environ.get("GITHUB_RUN_ID") or os.environ.get("CI_PIPELINE_ID") or "local")
    now = datetime.now(UTC).isoformat()
    current_run = {
        "run_id": run_id,
        "timestamp_utc": now,
        "issues": sorted(current_issues),
        "issue_count": len(current_issues),
    }
    updated_history = {
        "schema_version": HISTORY_SCHEMA_VERSION,
        "updated_at_utc": now,
        "counts": updated_counts,
        "runs": _updated_runs(history_payload, current_run),
    }
    _write_json(PERSISTENT_HISTORY, updated_history)

    # Snapshot history under the active evidence root for workflow artifact visibility.
    history_snapshot = sec / "ci_failure_classifier_history.json"
    _write_json(history_snapshot, updated_history)

    report = {
        "status": "PASS" if not current_issues and not findings else "WARN",
        "findings": findings,
        "summary": {
            "scanned_reports": scanned_reports,
            "current_issue_count": len(current_issues),
            "new_issue_count": len(new_issues),
            "recurring_issue_count": len(recurring_issues),
            "chronic_issue_count": len(chronic_issues),
            "resolved_since_last_count": len(resolved_since_last),
            "history_path": str(PERSISTENT_HISTORY.relative_to(ROOT)).replace("\\", "/"),
        },
        "classification": {
            "current_issues": sorted(current_issues),
            "new_issues": new_issues,
            "recurring_issues": recurring_issues,
            "chronic_issues": chronic_issues,
            "resolved_since_last": resolved_since_last,
            "top_recurring": top_recurring,
        },
        "metadata": {"gate": "ci_failure_classifier"},
    }
    out = sec / "ci_failure_classifier.json"
    write_json_report(out, report)
    print(f"CI_FAILURE_CLASSIFIER: {report['status']}")
    print(f"Report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
