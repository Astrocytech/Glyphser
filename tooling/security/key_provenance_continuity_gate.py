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
from tooling.security.report_io import write_json_report


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


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
    sec = evidence_root() / "security"
    policy = _load(sec / "policy_signature.json")
    provenance = _load(sec / "provenance_signature.json")
    attestation = _load(sec / "evidence_attestation_index.json")
    findings: list[str] = []

    sources = {
        "policy_signature": _key_provenance(policy),
        "provenance_signature": _key_provenance(provenance),
        "evidence_attestation_index": _key_provenance(attestation),
    }

    missing = sorted(name for name, kp in sources.items() if not kp)
    for name in missing:
        findings.append(f"missing_key_provenance:{name}")

    key_ids = {str(kp.get("key_id", "")).strip() for kp in sources.values() if kp}
    key_ids.discard("")
    if len(key_ids) > 1:
        findings.append(f"key_id_mismatch:{','.join(sorted(key_ids))}")

    adapters = {str(kp.get("adapter", "")).strip() for kp in sources.values() if kp}
    adapters.discard("")
    if len(adapters) > 1:
        findings.append(f"adapter_mismatch:{','.join(sorted(adapters))}")

    fallback_users = sorted(
        name for name, kp in sources.items() if isinstance(kp, dict) and bool(kp.get("fallback_used", False))
    )
    if fallback_users:
        findings.append(f"fallback_signing_used:{','.join(fallback_users)}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "sources": sorted(sources.keys()),
            "missing_sources": missing,
            "distinct_key_ids": sorted(key_ids),
            "distinct_adapters": sorted(adapters),
            "fallback_sources": fallback_users,
        },
        "metadata": {"gate": "key_provenance_continuity_gate"},
    }
    out = sec / "key_provenance_continuity_gate.json"
    write_json_report(out, report)
    print(f"KEY_PROVENANCE_CONTINUITY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
