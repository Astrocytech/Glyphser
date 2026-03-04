#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import json
import sys
from pathlib import Path

from runtime.glyphser.registry.interface_hash import compute_interface_hash
from tooling.quality_gates.telemetry import emit_gate_trace

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "evidence" / "gates" / "structure" / "spec_impl_congruence.json"
OPENAPI = ROOT / "specs" / "contracts" / "openapi_public_api_v1.yaml"
INTERFACE_HASH = ROOT / "specs" / "contracts" / "interface_hash.json"
REGISTRY = ROOT / "specs" / "contracts" / "operator_registry.json"

REQUIRED_ENDPOINTS = {
    "/v1/jobs",
    "/v1/jobs/{job_id}",
    "/v1/jobs/{job_id}/evidence",
    "/v1/jobs/{job_id}/replay",
}

REQUIRED_PUBLIC_EXPORTS = {
    "verify",
    "VerificationResult",
    "RuntimeApiConfig",
    "RuntimeService",
}

REQUIRED_RUNTIME_METHODS = {
    "submit_job",
    "status",
    "evidence",
    "replay",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate() -> dict:
    findings: list[str] = []

    openapi_doc = OPENAPI.read_text(encoding="utf-8")
    missing_endpoints = sorted([ep for ep in REQUIRED_ENDPOINTS if ep not in openapi_doc])
    if missing_endpoints:
        findings.append(f"missing_openapi_endpoints:{','.join(missing_endpoints)}")

    glyphser_mod = importlib.import_module("glyphser")
    public_exports = set(getattr(glyphser_mod, "__all__", []))
    missing_exports = sorted(REQUIRED_PUBLIC_EXPORTS - public_exports)
    if missing_exports:
        findings.append(f"missing_public_exports:{','.join(missing_exports)}")

    runtime_cls = getattr(glyphser_mod, "RuntimeService", None)
    missing_methods = sorted([m for m in REQUIRED_RUNTIME_METHODS if not hasattr(runtime_cls, m)])
    if missing_methods:
        findings.append(f"missing_runtime_methods:{','.join(missing_methods)}")

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    expected_interface_hash = json.loads(INTERFACE_HASH.read_text(encoding="utf-8")).get("interface_hash", "")
    actual_interface_hash = compute_interface_hash(registry)
    if expected_interface_hash != actual_interface_hash:
        findings.append("interface_hash_mismatch")

    payload = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "checks": {
            "openapi_sha256": _sha256(OPENAPI),
            "interface_hash_expected": expected_interface_hash,
            "interface_hash_actual": actual_interface_hash,
            "public_exports": sorted(public_exports),
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    emit_gate_trace(ROOT, "spec_impl_congruence", payload)
    return payload


def main() -> int:
    report = evaluate()
    if report["status"] == "PASS":
        print("SPEC_IMPL_CONGRUENCE_GATE: PASS")
        return 0
    print("SPEC_IMPL_CONGRUENCE_GATE: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
