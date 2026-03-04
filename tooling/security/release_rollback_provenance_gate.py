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


def _status(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return "INVALID"
    return str(payload.get("status", "UNKNOWN")).upper() if isinstance(payload, dict) else "INVALID"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    deploy = evidence_root() / "deploy" / "latest.json"
    rollback = evidence_root() / "deploy" / "rollback.json"
    statuses = {
        "deploy": _status(deploy),
        "rollback": _status(rollback),
        "provenance_signature": _status(sec / "provenance_signature.json"),
        "policy_signature": _status(sec / "policy_signature.json"),
    }
    findings = [f"{k}_not_pass" for k, v in statuses.items() if v != "PASS"]
    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": statuses,
        "metadata": {"gate": "release_rollback_provenance_gate"},
    }
    out = sec / "release_rollback_provenance_gate.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"RELEASE_ROLLBACK_PROVENANCE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
