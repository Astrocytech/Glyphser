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


def _report_name_from_cmd(cmd: list[str]) -> str | None:
    if len(cmd) < 2:
        return None
    script = Path(cmd[1]).name
    if not script.endswith(".py"):
        return None
    stem = script[:-3]
    if stem == "security_super_gate":
        return None
    return stem + ".json"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    super_path = sec / "security_super_gate.json"
    findings: list[str] = []
    checked = 0

    if not super_path.exists():
        findings.append("missing_security_super_gate_report")
        results: list[dict[str, object]] = []
    else:
        payload = json.loads(super_path.read_text(encoding="utf-8"))
        raw = payload.get("results", []) if isinstance(payload, dict) else []
        results = [r for r in raw if isinstance(r, dict)]

    for row in results:
        cmd = row.get("cmd", [])
        status = str(row.get("status", "")).upper()
        if not isinstance(cmd, list):
            continue
        report_name = _report_name_from_cmd([str(x) for x in cmd])
        if not report_name:
            continue
        report_path = sec / report_name
        checked += 1
        if not report_path.exists():
            findings.append(f"missing_component_report:{report_name}")
            continue
        try:
            component = json.loads(report_path.read_text(encoding="utf-8"))
        except Exception:
            findings.append(f"invalid_component_report_json:{report_name}")
            continue
        component_status = str(component.get("status", "")).upper()
        if component_status != status:
            findings.append(f"status_mismatch:{report_name}:{status}:{component_status or 'UNKNOWN'}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"checked_components": checked},
        "metadata": {"gate": "security_cross_gate_consistency_gate"},
    }
    out = sec / "security_cross_gate_consistency_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_CROSS_GATE_CONSISTENCY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
