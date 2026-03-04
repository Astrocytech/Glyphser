#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from tooling.lib.path_config import evidence_root

ROOT = Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    closure = evidence_root() / "security" / "post_incident_closure.json"
    skipped = False

    payload: dict[str, Any] = {}
    if closure.exists():
        loaded = json.loads(closure.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            payload = loaded
        else:
            findings.append("invalid_post_incident_closure_payload")
    else:
        skipped = True

    if payload:
        if str(payload.get("status", "")).upper() != "PASS":
            findings.append("post_incident_closure_not_pass")
        incident_id = str(payload.get("incident_id", "")).strip()
        if not incident_id:
            findings.append("missing_incident_id")
        items = payload.get("action_items", [])
        if not isinstance(items, list) or not items:
            findings.append("missing_action_items")
        else:
            for ix, item in enumerate(items):
                if not isinstance(item, dict):
                    findings.append(f"invalid_action_item:{ix}")
                    continue
                if not str(item.get("id", "")).strip():
                    findings.append(f"missing_action_item_id:{ix}")
                if not str(item.get("verification_test", "")).strip():
                    findings.append(f"missing_action_item_test:{ix}")
                if item.get("verified") is not True:
                    findings.append(f"action_item_not_verified:{ix}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "skipped": skipped,
            "closure_path": str(closure.relative_to(ROOT)).replace("\\", "/"),
            "action_item_count": len(payload.get("action_items", [])) if isinstance(payload, dict) else 0,
        },
        "metadata": {"gate": "post_incident_closure_gate"},
    }
    out = evidence_root() / "security" / "post_incident_closure_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"POST_INCIDENT_CLOSURE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
