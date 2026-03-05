#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report
CATALOG = ROOT / "governance" / "security" / "incident_regression_catalog.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    checked = 0

    if not CATALOG.exists():
        findings.append("missing_incident_regression_catalog")
        incidents: list[Any] = []
    else:
        try:
            payload = _load_json(CATALOG)
            raw = payload.get("incidents", [])
            incidents = raw if isinstance(raw, list) else []
            if not isinstance(raw, list):
                findings.append("invalid_incident_list")
        except Exception:
            incidents = []
            findings.append("invalid_incident_regression_catalog")

    for idx, item in enumerate(incidents, start=1):
        if not isinstance(item, dict):
            continue
        severity = str(item.get("severity", "")).strip().lower()
        if severity not in {"high", "critical"}:
            continue
        checked += 1
        incident_id = str(item.get("incident_id", f"idx-{idx}")).strip() or f"idx-{idx}"
        tests = item.get("regression_tests", [])
        if not isinstance(tests, list):
            findings.append(f"high_severity_missing_regression_test:{incident_id}")
            continue
        normalized = [str(x).strip() for x in tests if isinstance(x, str) and str(x).strip()]
        if not normalized:
            findings.append(f"high_severity_missing_regression_test:{incident_id}")
            continue
        if not any(t.startswith("tests/") for t in normalized):
            findings.append(f"high_severity_missing_permanent_test_reference:{incident_id}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "catalog_path": str(CATALOG.relative_to(ROOT)).replace("\\", "/"),
            "high_severity_incidents_checked": checked,
        },
        "metadata": {"gate": "high_severity_incident_regression_gate"},
    }
    out = evidence_root() / "security" / "high_severity_incident_regression_gate.json"
    write_json_report(out, report)
    print(f"HIGH_SEVERITY_INCIDENT_REGRESSION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
