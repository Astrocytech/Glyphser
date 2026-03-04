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


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    report = {
        "status": "PASS",
        "findings": [],
        "summary": {
            "policy_signature": _load(sec / "policy_signature.json").get("status", "MISSING"),
            "provenance_signature": _load(sec / "provenance_signature.json").get("status", "MISSING"),
            "attestation": _load(sec / "evidence_attestation_gate.json").get("status", "MISSING"),
            "slo": _load(sec / "security_slo_report.json").get("summary", {}),
        },
        "metadata": {"gate": "security_dashboard_export"},
    }
    out = sec / "security_dashboard.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"SECURITY_DASHBOARD_EXPORT: {report['status']}")
    print(f"Report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
