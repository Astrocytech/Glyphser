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

TRIGGER_GATE_REPORT = ROOT / "evidence" / "security" / "hardening_backlog_trigger_gate.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    candidates: list[dict[str, str]] = []

    if not TRIGGER_GATE_REPORT.exists():
        findings.append("missing_hardening_backlog_trigger_gate_report")
    else:
        report = _load_json(TRIGGER_GATE_REPORT)
        changed = report.get("changed_sources", [])
        if isinstance(changed, list):
            for row in changed:
                if not isinstance(row, dict):
                    continue
                source = str(row.get("path", "")).strip()
                if not source:
                    continue
                candidates.append(
                    {
                        "source": source,
                        "proposed_action": "append_trigger_backed_hardening_item",
                    }
                )

    triage = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "trigger_backed_candidates": len(candidates),
            "non_trigger_candidates": 0,
        },
        "metadata": {"report": "weekly_hardening_triage"},
        "candidates": candidates,
    }
    out = evidence_root() / "security" / "weekly_hardening_triage.json"
    write_json_report(out, triage)
    print(f"WEEKLY_HARDENING_TRIAGE: {triage['status']}")
    print(f"Report: {out}")
    return 0 if triage["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
