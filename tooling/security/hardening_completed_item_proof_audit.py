#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

REGISTRY = ROOT / "governance" / "security" / "hardening_pending_item_registry.json"
MIN_REGRESSION_GREEN_RUNS = int(os.environ.get("GLYPHSER_HARDENING_MIN_REGRESSION_GREEN_RUNS", "3") or "3")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _as_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    reopened = 0
    audited_done = 0

    if not REGISTRY.exists():
        findings.append("missing_hardening_pending_item_registry")
        entries: list[dict[str, Any]] = []
        payload: dict[str, Any] = {"schema_version": 1, "entries": entries}
    else:
        payload = _load_json(REGISTRY)
        raw = payload.get("entries", [])
        entries = [item for item in raw if isinstance(item, dict)] if isinstance(raw, list) else []

    for row in entries:
        status = str(row.get("status", "")).strip().lower()
        if status != "done":
            continue
        audited_done += 1
        item_id = str(row.get("id", "")).strip() or "unknown"
        missing = []
        if not str(row.get("code_diff_ref", "")).strip():
            missing.append("code_diff_ref")
        if not str(row.get("test_diff_ref", "")).strip():
            missing.append("test_diff_ref")
        if not str(row.get("ci_run_ref", "")).strip():
            missing.append("ci_run_ref")
        if not str(row.get("negative_test_evidence_ref", "")).strip():
            missing.append("negative_test_evidence_ref")
        if not str(row.get("evidence_link", "")).strip():
            missing.append("evidence_link")
        if _as_int(row.get("regression_green_runs", 0), 0) < MIN_REGRESSION_GREEN_RUNS:
            missing.append("regression_green_runs")
        if missing:
            findings.append(f"completed_item_missing_proof:{item_id}:{','.join(missing)}")
            row["previous_status"] = "done"
            row["status"] = "in_progress"
            reopened += 1

    if entries:
        payload["entries"] = entries
        REGISTRY.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "audited_done_items": audited_done,
            "reopened_items": reopened,
            "min_regression_green_runs": MIN_REGRESSION_GREEN_RUNS,
        },
        "metadata": {"process": "hardening_completed_item_proof_audit"},
    }
    out = evidence_root() / "security" / "hardening_completed_item_proof_audit.json"
    write_json_report(out, report)
    print(f"HARDENING_COMPLETED_ITEM_PROOF_AUDIT: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
