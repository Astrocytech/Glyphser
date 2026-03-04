#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root
from tooling.security.advanced_policy import load_policy
from tooling.security.report_io import write_json_report


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _key_provenance(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    meta = payload.get("metadata", {})
    if isinstance(meta, dict):
        kp = meta.get("key_provenance", {})
        if isinstance(kp, dict) and kp:
            return kp
    kp = payload.get("key_provenance", {})
    return kp if isinstance(kp, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = load_policy()
    forbidden = {str(x).strip().lower() for x in policy.get("forbidden_signature_adapters", []) if isinstance(x, str)}
    allowed = {str(x).strip().lower() for x in policy.get("allowed_signature_adapters", []) if isinstance(x, str)}
    sec = evidence_root() / "security"
    findings: list[str] = []
    checked = 0

    sources = {
        "policy_signature": _load(sec / "policy_signature.json"),
        "provenance_signature": _load(sec / "provenance_signature.json"),
        "evidence_attestation_index": _load(sec / "evidence_attestation_index.json"),
    }
    adapters: dict[str, str] = {}
    for name, payload in sources.items():
        kp = _key_provenance(payload)
        if not kp:
            findings.append(f"missing_key_provenance:{name}")
            continue
        adapter = str(kp.get("adapter", "")).strip().lower()
        if not adapter:
            findings.append(f"missing_signature_adapter:{name}")
            continue
        checked += 1
        adapters[name] = adapter
        if adapter in forbidden:
            findings.append(f"forbidden_signature_adapter:{name}:{adapter}")
        if allowed and adapter not in allowed:
            findings.append(f"signature_adapter_not_allowlisted:{name}:{adapter}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "checked_sources": checked,
            "adapters": adapters,
            "forbidden_signature_adapters": sorted(forbidden),
            "allowed_signature_adapters": sorted(allowed),
        },
        "metadata": {"gate": "signature_algorithm_policy_gate"},
    }
    out = sec / "signature_algorithm_policy_gate.json"
    write_json_report(out, report)
    print(f"SIGNATURE_ALGORITHM_POLICY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
