#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY = ROOT / "governance" / "security" / "promotion_policy.json"


def _status(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return "INVALID"
    return str(payload.get("status", "UNKNOWN")).upper() if isinstance(payload, dict) else "INVALID"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    if not isinstance(policy, dict):
        raise ValueError("invalid promotion policy")
    required = policy.get("canary_required_reports", policy.get("required_reports", []))
    if not isinstance(required, list):
        raise ValueError("invalid canary required reports policy")
    required_reports = [str(x).strip() for x in required if isinstance(x, str) and str(x).strip()]

    sec = evidence_root() / "security"
    statuses = {name: _status(sec / name) for name in required_reports}
    findings = [f"canary_required_report_not_pass:{name}:{status}" for name, status in statuses.items() if status != "PASS"]

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "canary_slice": "security-pre-promotion",
            "required_reports": required_reports,
            "statuses": statuses,
        },
        "metadata": {"gate": "canary_promotion_guard"},
    }
    out = sec / "canary_promotion_guard.json"
    write_json_report(out, report)
    print(f"CANARY_PROMOTION_GUARD: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
