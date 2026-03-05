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

RELEASE_CRITICAL_REPORTS = {
    "security_super_gate": "security/security_super_gate.json",
    "policy_signature": "security/policy_signature.json",
    "provenance_signature": "security/provenance_signature.json",
    "evidence_attestation_gate": "security/evidence_attestation_gate.json",
}


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _rag(status: str) -> str:
    normalized = status.upper()
    if normalized == "PASS":
        return "green"
    if normalized == "WARN":
        return "amber"
    if normalized in {"FAIL", "MISSING"}:
        return "red"
    return "amber"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    ev = evidence_root()
    findings: list[str] = []
    rows: list[dict[str, str]] = []

    for control, rel in RELEASE_CRITICAL_REPORTS.items():
        path = ev / rel
        relpath = str(path.relative_to(ROOT)).replace("\\", "/")
        if not path.exists():
            status = "MISSING"
            findings.append(f"missing_control_report:{control}:{relpath}")
        else:
            try:
                status = str(_load_json(path).get("status", "UNKNOWN")).upper()
            except Exception:
                status = "UNKNOWN"
                findings.append(f"invalid_control_report:{control}:{relpath}")
        rows.append({"control": control, "status": status, "rag": _rag(status), "path": relpath})

    red = sum(1 for row in rows if row["rag"] == "red")
    amber = sum(1 for row in rows if row["rag"] == "amber")
    green = sum(1 for row in rows if row["rag"] == "green")
    overall = "red" if red > 0 else ("amber" if amber > 0 else "green")

    report = {
        "status": "PASS" if overall == "green" and not findings else "FAIL",
        "findings": findings,
        "summary": {"overall_rag": overall, "red": red, "amber": amber, "green": green},
        "metadata": {"gate": "control_posture_rag_export"},
        "controls": rows,
    }
    out = ev / "security" / "control_posture_rag_export.json"
    write_json_report(out, report)
    print(f"CONTROL_POSTURE_RAG_EXPORT: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
