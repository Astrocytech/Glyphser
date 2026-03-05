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

POLICY = ROOT / "tooling" / "security" / "stale_security_fixture_policy.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not POLICY.exists():
        findings.append("missing_stale_security_fixture_policy")
        policy: dict[str, Any] = {}
    else:
        try:
            policy = _load_json(POLICY)
        except Exception:
            policy = {}
            findings.append("invalid_stale_security_fixture_policy")

    max_fixture_lag_days = float(policy.get("max_fixture_lag_days", 14.0)) if isinstance(policy, dict) else 14.0
    tracked = policy.get("tracked_gate_fixtures", []) if isinstance(policy, dict) else []
    if not isinstance(tracked, list):
        tracked = []
        findings.append("invalid_tracked_gate_fixtures")

    checked_fixtures = 0
    stale_fixtures = 0
    for item in tracked:
        if not isinstance(item, dict):
            findings.append("invalid_tracked_gate_fixture_entry")
            continue
        gate_rel = str(item.get("gate", "")).strip()
        raw_fixtures = item.get("fixtures", [])
        if not gate_rel or not isinstance(raw_fixtures, list) or not raw_fixtures:
            findings.append("invalid_tracked_gate_fixture_mapping")
            continue

        gate = ROOT / gate_rel
        if not gate.exists():
            findings.append(f"missing_gate_script:{gate_rel}")
            continue

        for fixture_item in raw_fixtures:
            fixture_rel = str(fixture_item).strip()
            if not fixture_rel:
                findings.append("invalid_fixture_path_entry")
                continue
            checked_fixtures += 1
            fixture = ROOT / fixture_rel
            if not fixture.exists():
                findings.append(f"missing_fixture_file:{fixture_rel}")
                continue

            fixture_lag_days = (gate.stat().st_mtime - fixture.stat().st_mtime) / 86400.0
            if fixture_lag_days > max_fixture_lag_days:
                stale_fixtures += 1
                findings.append(
                    f"stale_fixture_after_gate_change:{gate_rel}:{fixture_rel}:{fixture_lag_days:.1f}d"
                )

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "tracked_gate_entries": len(tracked),
            "checked_fixtures": checked_fixtures,
            "stale_fixture_count": stale_fixtures,
            "max_fixture_lag_days": max_fixture_lag_days,
        },
        "metadata": {"gate": "stale_security_fixture_gate"},
    }
    out = evidence_root() / "security" / "stale_security_fixture_gate.json"
    write_json_report(out, report)
    print(f"STALE_SECURITY_FIXTURE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
