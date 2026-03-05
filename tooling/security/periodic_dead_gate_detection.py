#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

WORKFLOW_DIR = ROOT / ".github" / "workflows"
SECURITY_DIR = ROOT / "tooling" / "security"
STATE = ROOT / "evidence" / "security" / "periodic_dead_gate_detection_state.json"
MAX_INTERVAL_DAYS = 30
RUN_RE = re.compile(r"python\s+tooling/security/([A-Za-z0-9_.-]+\.py)")


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
    now = _now_utc()

    gates = sorted(path.name for path in SECURITY_DIR.glob("*_gate.py"))
    wired: set[str] = set()
    for wf in WORKFLOW_DIR.glob("*.yml"):
        text = wf.read_text(encoding="utf-8")
        for match in RUN_RE.findall(text):
            wired.add(match)
    dead = sorted(gate for gate in gates if gate not in wired)
    findings.extend(f"dead_gate_not_wired:{gate}" for gate in dead)

    if STATE.exists():
        try:
            previous = _load_json(STATE)
            last = str(previous.get("last_scan_utc", "")).strip()
            if last:
                last_dt = datetime.fromisoformat(last)
                age_days = (now - last_dt).total_seconds() / 86400.0
                if age_days > MAX_INTERVAL_DAYS:
                    findings.append(f"dead_gate_periodic_scan_stale:{age_days:.1f}d>{MAX_INTERVAL_DAYS}d")
        except Exception:
            findings.append("invalid_periodic_dead_gate_detection_state")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "total_gates": len(gates),
            "dead_gates": len(dead),
            "max_interval_days": MAX_INTERVAL_DAYS,
            "scanned_at_utc": now.isoformat(),
        },
        "metadata": {"gate": "periodic_dead_gate_detection"},
        "dead_gates": dead,
    }
    out = evidence_root() / "security" / "periodic_dead_gate_detection.json"
    write_json_report(out, report)
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps({"last_scan_utc": now.isoformat()}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PERIODIC_DEAD_GATE_DETECTION: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
