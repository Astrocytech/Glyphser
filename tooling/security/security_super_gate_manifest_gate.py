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

MANIFEST = ROOT / "tooling" / "security" / "security_super_gate_manifest.json"
SUPER_GATE = ROOT / "tooling" / "security" / "security_super_gate.py"


def _check_order(text: str, snippets: list[str], label: str) -> list[str]:
    findings: list[str] = []
    pos = -1
    for snippet in snippets:
        idx = text.find(snippet)
        if idx < 0:
            findings.append(f"missing_{label}_snippet:{snippet}")
            continue
        if idx < pos:
            findings.append(f"out_of_order_{label}_snippet:{snippet}")
        pos = max(pos, idx)
    return findings


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("invalid super gate manifest")
    core = payload.get("core", [])
    extended = payload.get("extended", [])
    if not isinstance(core, list) or not all(isinstance(x, str) for x in core):
        raise ValueError("manifest core list invalid")
    if not isinstance(extended, list) or not all(isinstance(x, str) for x in extended):
        raise ValueError("manifest extended list invalid")

    text = SUPER_GATE.read_text(encoding="utf-8")
    findings.extend(_check_order(text, core, "core"))
    findings.extend(_check_order(text, extended, "extended"))
    if len(set(core)) != len(core):
        findings.append("duplicate_core_manifest_entries")
    if len(set(extended)) != len(extended):
        findings.append("duplicate_extended_manifest_entries")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"core_entries": len(core), "extended_entries": len(extended)},
        "metadata": {"gate": "security_super_gate_manifest_gate"},
    }
    out = evidence_root() / "security" / "security_super_gate_manifest_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_SUPER_GATE_MANIFEST_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
