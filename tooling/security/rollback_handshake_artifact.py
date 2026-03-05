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

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
current_key = artifact_signing.current_key
sign_file = artifact_signing.sign_file
verify_file = artifact_signing.verify_file
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

REQUIRED_REVALIDATIONS = {
    "provenance_signature": "provenance_signature.json",
    "policy_signature": "policy_signature.json",
    "rollback_provenance_gate": "release_rollback_provenance_gate.json",
}


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _status(payload: dict[str, Any]) -> str:
    return str(payload.get("status", "")).strip().upper()


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    sec = evidence_root() / "security"

    checks: list[dict[str, str]] = []
    for check_id, filename in REQUIRED_REVALIDATIONS.items():
        path = sec / filename
        if not path.exists():
            findings.append(f"missing_revalidation_artifact:{filename}")
            checks.append({"check": check_id, "path": filename, "status": "MISSING"})
            continue
        payload = _load_json(path)
        status = _status(payload)
        checks.append({"check": check_id, "path": filename, "status": status or "UNKNOWN"})
        if status != "PASS":
            findings.append(f"revalidation_not_pass:{check_id}:{status or 'UNKNOWN'}")

    artifact = {
        "status": "PASS" if not findings else "FAIL",
        "required_revalidations": list(REQUIRED_REVALIDATIONS.keys()),
        "checks": checks,
    }
    artifact_path = sec / "rollback_handshake_artifact.json"
    write_json_report(artifact_path, artifact)

    sig_path = artifact_path.with_suffix(".json.sig")
    sig = sign_file(artifact_path, key=current_key(strict=False))
    sig_path.write_text(sig + "\n", encoding="utf-8")
    if not verify_file(artifact_path, sig, key=current_key(strict=False)):
        findings.append("rollback_handshake_artifact_signature_invalid")

    gate = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "required_checks": len(REQUIRED_REVALIDATIONS),
            "passed_checks": sum(1 for item in checks if item.get("status") == "PASS"),
        },
        "metadata": {"gate": "rollback_handshake_artifact"},
    }
    out = sec / "rollback_handshake_artifact_gate.json"
    write_json_report(out, gate)
    print(f"ROLLBACK_HANDSHAKE_ARTIFACT: {gate['status']}")
    print(f"Artifact: {artifact_path}")
    print(f"Gate: {out}")
    return 0 if gate["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
