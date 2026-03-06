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

SIGNATURE_SOURCES = [
    {
        "gate": "policy_signature_gate",
        "script_path": "tooling/security/policy_signature_gate.py",
        "report_path": "evidence/security/policy_signature.json",
    },
    {
        "gate": "provenance_signature_gate",
        "script_path": "tooling/security/provenance_signature_gate.py",
        "report_path": "evidence/security/provenance_signature.json",
    },
    {
        "gate": "evidence_attestation_index",
        "script_path": "tooling/security/evidence_attestation_index.py",
        "report_path": "evidence/security/evidence_attestation_index.json",
    },
    {
        "gate": "evidence_attestation_gate",
        "script_path": "tooling/security/evidence_attestation_gate.py",
        "report_path": "evidence/security/evidence_attestation_gate.json",
    },
]


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"invalid json object: {path}")
    return payload


def _key_provenance(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    metadata = payload.get("metadata", {})
    if isinstance(metadata, dict):
        kp = metadata.get("key_provenance", {})
        if isinstance(kp, dict) and kp:
            return kp
    kp = payload.get("key_provenance", {})
    return kp if isinstance(kp, dict) else {}


def _key_mode(kp: dict[str, Any]) -> str:
    if bool(kp.get("fallback_used", False)):
        return "fallback"
    source = str(kp.get("source", "")).strip()
    if source:
        return source
    adapter = str(kp.get("adapter", "")).strip()
    if adapter:
        return adapter
    return "unknown"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    ledger: list[dict[str, Any]] = []
    sec = evidence_root() / "security"

    for source in SIGNATURE_SOURCES:
        report_rel = str(source["report_path"])
        report_abs = ROOT / report_rel
        if not report_abs.exists():
            findings.append(f"missing_signature_report:{source['gate']}:{report_rel}")
            continue
        payload = _load_json(report_abs)
        kp = _key_provenance(payload)
        if not kp:
            findings.append(f"missing_key_provenance:{source['gate']}:{report_rel}")
            continue
        ledger.append(
            {
                "gate": source["gate"],
                "script_path": source["script_path"],
                "report_path": report_rel,
                "key_mode": _key_mode(kp),
                "key_adapter": str(kp.get("adapter", "")).strip(),
                "key_source": str(kp.get("source", "")).strip(),
                "fallback_used": bool(kp.get("fallback_used", False)),
                "key_id": str(kp.get("key_id", "")).strip(),
            }
        )

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "ledger_entries": len(ledger),
            "signature_sources_expected": len(SIGNATURE_SOURCES),
            "fallback_entries": sum(1 for item in ledger if bool(item.get("fallback_used", False))),
        },
        "metadata": {"gate": "key_usage_ledger"},
        "ledger": ledger,
    }
    out = sec / "key_usage_ledger.json"
    write_json_report(out, report)
    print(f"KEY_USAGE_LEDGER: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
