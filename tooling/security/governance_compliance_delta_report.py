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

BASELINE_POLICY = ROOT / "governance" / "security" / "governance_compliance_baseline.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("payload is not an object")
    return payload


def _resolve_baseline_path() -> Path:
    configured = os.environ.get("GLYPHSER_COMPLIANCE_BASELINE_PATH", "").strip()
    return Path(configured).expanduser() if configured else BASELINE_POLICY


def _evaluate_control(control: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    control_id = str(control.get("id", "")).strip()
    rel_path = str(control.get("path", "")).strip()
    ctype = str(control.get("type", "file_exists")).strip() or "file_exists"
    expected_status = str(control.get("expected_status", "PASS")).strip().upper() or "PASS"

    if not control_id:
        return False, {"id": "", "reason": "invalid_control_missing_id"}
    if not rel_path:
        return False, {"id": control_id, "reason": "invalid_control_missing_path"}

    target = ROOT / rel_path
    item: dict[str, Any] = {
        "id": control_id,
        "description": str(control.get("description", "")).strip(),
        "type": ctype,
        "path": rel_path,
        "expected": {"exists": True} if ctype == "file_exists" else {"status": expected_status},
        "observed": {},
    }

    if ctype == "file_exists":
        exists = target.exists()
        item["observed"] = {"exists": exists}
        if exists:
            return True, item
        item["reason"] = "missing_required_file"
        return False, item

    if ctype == "json_status":
        if not target.exists():
            item["observed"] = {"status": "MISSING"}
            item["reason"] = "missing_required_json_report"
            return False, item
        try:
            payload = _load_json(target)
        except Exception:
            item["observed"] = {"status": "INVALID_JSON"}
            item["reason"] = "invalid_json_report"
            return False, item
        status = str(payload.get("status", "UNKNOWN")).upper()
        item["observed"] = {"status": status}
        if status == expected_status:
            return True, item
        item["reason"] = "unexpected_report_status"
        return False, item

    item["reason"] = f"unknown_control_type:{ctype}"
    return False, item


def main(argv: list[str] | None = None) -> int:
    _ = argv
    baseline_path = _resolve_baseline_path()
    findings: list[str] = []

    if not baseline_path.exists():
        findings.append(f"missing_baseline:{baseline_path}")
        baseline: dict[str, Any] = {}
    else:
        try:
            baseline = _load_json(baseline_path)
        except Exception as exc:
            findings.append(f"invalid_baseline:{exc}")
            baseline = {}

    controls = baseline.get("controls", []) if isinstance(baseline, dict) else []
    if baseline and (not isinstance(controls, list) or not all(isinstance(item, dict) for item in controls)):
        findings.append("invalid_baseline_controls")
        controls = []

    evaluated: list[dict[str, Any]] = []
    delta: list[dict[str, Any]] = []
    for control in controls:
        ok, item = _evaluate_control(control)
        evaluated.append(item)
        if not ok:
            delta.append(item)

    total = len(evaluated)
    compliant = total - len(delta)
    compliance_pct = 100.0 if total == 0 else round((compliant / total) * 100.0, 2)

    status = "FAIL" if findings else ("PASS" if not delta else "WARN")
    report = {
        "status": status,
        "findings": findings,
        "summary": {
            "baseline_path": str(baseline_path),
            "required_controls": total,
            "compliant_controls": compliant,
            "delta_controls": len(delta),
            "compliance_pct": compliance_pct,
        },
        "metadata": {
            "gate": "governance_compliance_delta_report",
            "schema_version": int(baseline.get("schema_version", 1)) if isinstance(baseline, dict) else 1,
        },
        "controls": evaluated,
        "delta": delta,
    }
    out = evidence_root() / "security" / "governance_compliance_delta_report.json"
    write_json_report(out, report)
    print(f"GOVERNANCE_COMPLIANCE_DELTA_REPORT: {report['status']}")
    print(f"Report: {out}")
    return 1 if report["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
