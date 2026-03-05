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

POLICY = ROOT / "governance" / "security" / "hardening_priority_rubric.json"
REGISTRY = ROOT / "governance" / "security" / "hardening_pending_item_registry.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    policy = _load_json(POLICY) if POLICY.exists() else {}
    allowed = {str(item).strip() for item in policy.get("allowed_priorities", []) if str(item).strip()} if isinstance(policy.get("allowed_priorities", []), list) else set()
    if not allowed:
        findings.append("missing_allowed_priorities")
    registry = _load_json(REGISTRY) if REGISTRY.exists() else {}
    entries = registry.get("entries", []) if isinstance(registry.get("entries", []), list) else []
    for row in entries:
        if not isinstance(row, dict):
            continue
        item_id = str(row.get("id", "")).strip()
        priority = str(row.get("priority", "")).strip()
        if priority not in allowed:
            findings.append(f"invalid_priority:{item_id or 'unknown'}:{priority or 'empty'}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"entries_checked": len(entries), "allowed_priorities": sorted(allowed)},
        "metadata": {"gate": "hardening_priority_rubric_gate"},
    }
    out = evidence_root() / "security" / "hardening_priority_rubric_gate.json"
    write_json_report(out, report)
    print(f"HARDENING_PRIORITY_RUBRIC_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
