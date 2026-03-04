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
        p = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return p if isinstance(p, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    gates = {
        "policy_signature": _load(sec / "policy_signature.json").get("status", "MISSING"),
        "provenance_signature": _load(sec / "provenance_signature.json").get("status", "MISSING"),
        "attestation": _load(sec / "evidence_attestation_gate.json").get("status", "MISSING"),
        "super_gate": _load(sec / "security_super_gate.json").get("status", "MISSING"),
    }
    pass_rate = sum(1 for v in gates.values() if str(v).upper() == "PASS") / max(1, len(gates))
    report = {
        "status": "PASS" if pass_rate >= 0.99 else "FAIL",
        "findings": [] if pass_rate >= 0.99 else [f"security_slo_pass_rate_below_target:{pass_rate:.2%}"],
        "summary": {"pass_rate": pass_rate, "target": 0.99, "gates": gates},
        "metadata": {"gate": "security_slo_report"},
    }
    out = sec / "security_slo_report.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"SECURITY_SLO_REPORT: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
