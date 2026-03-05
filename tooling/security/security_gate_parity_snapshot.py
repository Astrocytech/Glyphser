#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import json
import platform
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root

TARGET_REPORTS = [
    "policy_signature.json",
    "security_unsigned_json_gate.json",
    "provenance_signature.json",
    "security_event_schema_gate.json",
    "runtime_api_scope_matrix_gate.json",
    "security_super_gate.json",
]


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _normalize_report(payload: dict[str, Any]) -> dict[str, Any]:
    findings = payload.get("findings", [])
    findings_list = []
    if isinstance(findings, list):
        findings_list = sorted(str(item) for item in findings)
    return {
        "status": str(payload.get("status", "")).strip(),
        "findings": findings_list,
    }


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    normalized: dict[str, dict[str, Any]] = {}
    missing: list[str] = []
    for name in TARGET_REPORTS:
        path = sec / name
        if not path.exists():
            missing.append(name)
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            missing.append(name)
            continue
        if not isinstance(payload, dict):
            missing.append(name)
            continue
        normalized[name] = _normalize_report(payload)

    material = {"reports": normalized, "missing": sorted(missing)}
    parity_hash = hashlib.sha256(_canonical_json(material).encode("utf-8")).hexdigest()
    out_payload = {
        "schema_version": 1,
        "python_version": platform.python_version(),
        "normalized_reports": normalized,
        "missing_reports": sorted(missing),
        "parity_hash": parity_hash,
    }
    out = sec / "security_gate_parity_snapshot.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(out_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("SECURITY_GATE_PARITY_SNAPSHOT: PASS")
    print(f"Snapshot: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
