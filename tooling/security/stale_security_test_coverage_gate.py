#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY = ROOT / "governance" / "security" / "stale_security_test_coverage_policy.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not POLICY.exists():
        findings.append("missing_stale_security_test_coverage_policy")
        policy: dict[str, Any] = {}
    else:
        try:
            policy = _load_json(POLICY)
        except Exception:
            policy = {}
            findings.append("invalid_stale_security_test_coverage_policy")

    max_test_age_days = float(policy.get("max_test_age_days", 180.0)) if isinstance(policy, dict) else 180.0
    tracked = policy.get("tracked_scripts", []) if isinstance(policy, dict) else []
    if not isinstance(tracked, list):
        tracked = []
        findings.append("invalid_tracked_scripts")

    now = time.time()
    checked = 0
    stale = 0
    for item in tracked:
        if not isinstance(item, dict):
            findings.append("invalid_tracked_script_entry")
            continue
        script_rel = str(item.get("script", "")).strip()
        test_rel = str(item.get("test", "")).strip()
        if not script_rel or not test_rel:
            findings.append("invalid_tracked_script_mapping")
            continue
        script = ROOT / script_rel
        test = ROOT / test_rel
        checked += 1
        if not script.exists():
            findings.append(f"missing_script:{script_rel}")
            continue
        if not test.exists():
            findings.append(f"missing_test:{test_rel}")
            continue
        age_days = (now - test.stat().st_mtime) / 86400.0
        if age_days > max_test_age_days:
            stale += 1
            findings.append(f"stale_test_coverage:{script_rel}:{test_rel}:{age_days:.1f}d")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "tracked_scripts": checked,
            "stale_test_coverage_count": stale,
            "max_test_age_days": max_test_age_days,
        },
        "metadata": {"gate": "stale_security_test_coverage_gate"},
    }
    out = evidence_root() / "security" / "stale_security_test_coverage_gate.json"
    write_json_report(out, report)
    print(f"STALE_SECURITY_TEST_COVERAGE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
