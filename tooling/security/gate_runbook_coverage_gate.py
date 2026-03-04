#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from tooling.lib.path_config import evidence_root
from tooling.security.report_io import write_json_report

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "tooling" / "security" / "security_super_gate_manifest.json"
RUNBOOK = ROOT / "governance" / "security" / "GATE_RUNBOOK_INDEX.md"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    core = payload.get("core", []) if isinstance(payload, dict) else []
    ext = payload.get("extended", []) if isinstance(payload, dict) else []
    all_gates = [*core, *ext]
    text = RUNBOOK.read_text(encoding="utf-8") if RUNBOOK.exists() else ""
    if not text:
        findings.append("missing_or_empty_runbook_index")

    for rel in all_gates:
        name = Path(str(rel)).name
        marker = f"## `{name}`"
        if marker not in text:
            findings.append(f"missing_runbook_section:{name}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"gates_in_manifest": len(all_gates)},
        "metadata": {"gate": "gate_runbook_coverage_gate"},
    }
    out = evidence_root() / "security" / "gate_runbook_coverage_gate.json"
    write_json_report(out, report)
    print(f"GATE_RUNBOOK_COVERAGE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
