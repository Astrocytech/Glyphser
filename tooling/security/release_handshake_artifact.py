#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import sys
from datetime import UTC, datetime
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


def _acknowledged(value: str) -> bool:
    return value.strip().lower() in {"ack", "acknowledged", "yes", "true", "1"}


def _entry(*, role: str, owner: str, ack_value: str, timestamp: str) -> dict[str, Any]:
    return {
        "role": role,
        "owner": owner,
        "ack_value": ack_value,
        "acknowledged": _acknowledged(ack_value),
        "acknowledged_at": timestamp,
    }


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    timestamp = datetime.now(UTC).isoformat()

    security_owner = os.environ.get("GLYPHSER_SECURITY_OWNER", "").strip()
    release_owner = os.environ.get("GLYPHSER_RELEASE_OWNER", "").strip()
    security_ack = os.environ.get("GLYPHSER_RELEASE_HANDSHAKE_SECURITY_ACK", "").strip()
    release_ack = os.environ.get("GLYPHSER_RELEASE_HANDSHAKE_RELEASE_ACK", "").strip()

    if not security_owner:
        findings.append("missing_security_owner")
    if not release_owner:
        findings.append("missing_release_owner")
    if not _acknowledged(security_ack):
        findings.append("missing_security_owner_acknowledgment")
    if not _acknowledged(release_ack):
        findings.append("missing_release_owner_acknowledgment")

    handshake = {
        "status": "PASS" if not findings else "FAIL",
        "required_roles": ["security", "release"],
        "acknowledgments": [
            _entry(role="security", owner=security_owner, ack_value=security_ack, timestamp=timestamp),
            _entry(role="release", owner=release_owner, ack_value=release_ack, timestamp=timestamp),
        ],
    }
    artifact_path = evidence_root() / "security" / "release_handshake_artifact.json"
    write_json_report(artifact_path, handshake)

    sig_path = artifact_path.with_suffix(".json.sig")
    sig = sign_file(artifact_path, key=current_key(strict=False))
    sig_path.write_text(sig + "\n", encoding="utf-8")
    if not verify_file(artifact_path, sig, key=current_key(strict=False)):
        findings.append("release_handshake_artifact_signature_invalid")

    gate = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "required_roles": 2,
            "acknowledged_roles": int(_acknowledged(security_ack)) + int(_acknowledged(release_ack)),
        },
        "metadata": {"gate": "release_handshake_artifact"},
    }
    out = evidence_root() / "security" / "release_handshake_artifact_gate.json"
    write_json_report(out, gate)
    print(f"RELEASE_HANDSHAKE_ARTIFACT: {gate['status']}")
    print(f"Artifact: {artifact_path}")
    print(f"Gate: {out}")
    return 0 if gate["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
