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


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def _consumed_artifacts(super_gate: dict[str, Any]) -> set[str]:
    consumed = {"security/security_super_gate.json"}
    for row in super_gate.get("results", []):
        if not isinstance(row, dict):
            continue
        cmd = row.get("cmd", [])
        if not isinstance(cmd, list) or len(cmd) < 2:
            continue
        script = Path(str(cmd[1]))
        if script.suffix != ".py":
            continue
        consumed.add(f"security/{script.stem}.json")
    return consumed


def _lineage_references(lineage: dict[str, Any]) -> set[str]:
    refs: set[str] = set()
    for mapping in lineage.get("mappings", []):
        if not isinstance(mapping, dict):
            continue
        report = mapping.get("report")
        if isinstance(report, str) and report.startswith("security/"):
            refs.add(report)
        for src in mapping.get("source_artifacts", []):
            if isinstance(src, str) and src.startswith("security/"):
                refs.add(src)
    return refs


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    findings: list[str] = []

    super_gate = _load_json(sec / "security_super_gate.json")
    if super_gate is None:
        findings.append("missing_or_invalid:security/security_super_gate.json")
        super_gate = {}
    lineage = _load_json(sec / "security_lineage_map.json")
    if lineage is None:
        findings.append("missing_or_invalid:security/security_lineage_map.json")
        lineage = {}

    consumed = _consumed_artifacts(super_gate)
    referenced = _lineage_references(lineage)
    missing_refs = sorted(consumed - referenced)
    findings.extend(f"missing_lineage_reference:{path}" for path in missing_refs)

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "consumed_artifacts": len(consumed),
            "lineage_referenced_artifacts": len(referenced),
            "missing_references": len(missing_refs),
        },
        "metadata": {"gate": "security_lineage_consistency_gate"},
    }
    out = sec / "security_lineage_consistency_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_LINEAGE_CONSISTENCY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
