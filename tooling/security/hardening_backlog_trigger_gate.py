#!/usr/bin/env python3
from __future__ import annotations

import hashlib
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

STATE = ROOT / "governance" / "security" / "hardening_backlog_trigger_state.json"
TODO = ROOT / "glyphser_security_hardening_master_todo.txt"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    changed_sources: list[dict[str, str]] = []
    done_marker_present = False

    if TODO.exists():
        done_marker_present = any(line.strip() == "DONE" for line in TODO.read_text(encoding="utf-8").splitlines())

    if not STATE.exists():
        findings.append("missing_hardening_backlog_trigger_state")
        state_sources: list[dict[str, str]] = []
    else:
        payload = _load_json(STATE)
        raw = payload.get("sources", [])
        state_sources = [item for item in raw if isinstance(item, dict)] if isinstance(raw, list) else []

    for item in state_sources:
        rel = str(item.get("path", "")).strip()
        expected = str(item.get("sha256", "")).strip().lower()
        if not rel or len(expected) != 64:
            findings.append("invalid_trigger_state_entry")
            continue
        path = ROOT / rel
        if not path.exists():
            findings.append(f"missing_trigger_source:{rel}")
            continue
        observed = _sha256(path)
        if observed != expected:
            changed_sources.append({"path": rel, "expected_sha256": expected, "observed_sha256": observed})
            findings.append(f"new_trigger_detected_append_items_required:{rel}")

    if done_marker_present and changed_sources:
        findings.append("done_marker_must_not_be_present_on_new_trigger")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "sources_checked": len(state_sources),
            "changed_sources": len(changed_sources),
            "done_marker_present": done_marker_present,
        },
        "metadata": {"gate": "hardening_backlog_trigger_gate"},
        "changed_sources": changed_sources,
    }
    out = evidence_root() / "security" / "hardening_backlog_trigger_gate.json"
    write_json_report(out, report)
    print(f"HARDENING_BACKLOG_TRIGGER_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
