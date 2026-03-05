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


def _adapter(payload: dict[str, Any]) -> str:
    meta = payload.get("metadata", {})
    if isinstance(meta, dict):
        kp = meta.get("key_provenance", {})
        if isinstance(kp, dict) and kp:
            return str(kp.get("adapter", "")).strip().lower()
    kp = payload.get("key_provenance", {})
    if isinstance(kp, dict):
        return str(kp.get("adapter", "")).strip().lower()
    return ""


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    findings: list[str] = []

    sources = {
        "policy_signature": _load(sec / "policy_signature.json"),
        "provenance_signature": _load(sec / "provenance_signature.json"),
        "evidence_attestation_index": _load(sec / "evidence_attestation_index.json"),
    }
    adapters = {name: _adapter(payload) for name, payload in sources.items()}
    adapters = {name: adapter for name, adapter in adapters.items() if adapter}

    if not adapters:
        findings.append("no_signing_adapters_available_for_rehearsal")
    simulated_forbidden = sorted(set(adapters.values()))
    simulated_failures: list[str] = []
    for name, adapter in adapters.items():
        if adapter in simulated_forbidden:
            simulated_failures.append(f"simulated_forbidden_signature_adapter:{name}:{adapter}")
    if adapters and len(simulated_failures) != len(adapters):
        findings.append("unexpected_rehearsal_result:expected_all_sources_to_fail_when_forbidden")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings + simulated_failures,
        "summary": {
            "sources_checked": len(adapters),
            "simulated_forbidden_adapters": simulated_forbidden,
            "simulated_failures": len(simulated_failures),
        },
        "metadata": {"gate": "algorithm_deprecation_rehearsal_lane"},
    }
    out = sec / "algorithm_deprecation_rehearsal_lane.json"
    write_json_report(out, report)
    print(f"ALGORITHM_DEPRECATION_REHEARSAL_LANE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
