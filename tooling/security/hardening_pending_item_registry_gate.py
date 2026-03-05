#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

TODO = ROOT / "glyphser_security_hardening_master_todo.txt"
REGISTRY = ROOT / "governance" / "security" / "hardening_pending_item_registry.json"
ID_RE = re.compile(r"^SEC-HARD-(\d{4,})$")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _pending_count() -> int:
    if not TODO.exists():
        return 0
    total = 0
    for raw in TODO.read_text(encoding="utf-8").splitlines():
        if raw.strip().startswith("[ ]"):
            total += 1
    return total


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    pending_count = _pending_count()

    if not REGISTRY.exists():
        findings.append("missing_hardening_pending_item_registry")
        entries: list[dict[str, Any]] = []
    else:
        payload = _load_json(REGISTRY)
        raw = payload.get("entries", [])
        entries = [item for item in raw if isinstance(item, dict)] if isinstance(raw, list) else []

    ids: set[str] = set()
    for idx, row in enumerate(entries):
        item_id = str(row.get("id", "")).strip()
        if not ID_RE.match(item_id):
            findings.append(f"invalid_pending_item_id:{idx}")
        elif item_id in ids:
            findings.append(f"duplicate_pending_item_id:{item_id}")
        ids.add(item_id)

        for field in (
            "owner",
            "priority",
            "milestone",
            "target_date",
            "dependencies",
            "verification",
            "evidence_link",
            "status",
            "previous_status",
            "verification_proof",
            "code_diff_ref",
            "test_diff_ref",
            "ci_run_ref",
            "negative_test_evidence_ref",
            "regression_green_runs",
        ):
            if field not in row:
                findings.append(f"missing_pending_item_field:{idx}:{field}")

    if len(entries) != pending_count:
        findings.append(f"pending_registry_count_mismatch:todo={pending_count}:registry={len(entries)}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"todo_pending_items": pending_count, "registry_entries": len(entries)},
        "metadata": {"gate": "hardening_pending_item_registry_gate"},
    }
    out = evidence_root() / "security" / "hardening_pending_item_registry_gate.json"
    write_json_report(out, report)
    print(f"HARDENING_PENDING_ITEM_REGISTRY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
