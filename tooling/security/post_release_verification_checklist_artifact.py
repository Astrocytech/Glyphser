#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
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

DEFAULT_MANDATORY_UPLOADS = [
    "policy_signature.json",
    "provenance_signature.json",
    "slsa_provenance_v1.json",
    "security_super_gate.json",
    "promotion_policy_gate.json",
    "release_handshake_artifact_gate.json",
    "release_rollback_provenance_gate.json",
]


def _parse_required(raw: str) -> list[str]:
    text = raw.strip()
    if not text:
        return list(DEFAULT_MANDATORY_UPLOADS)
    try:
        payload = json.loads(text)
    except Exception:
        payload = [item.strip() for item in text.split(",") if item.strip()]
    if not isinstance(payload, list):
        return list(DEFAULT_MANDATORY_UPLOADS)
    out: list[str] = []
    for item in payload:
        value = str(item).strip()
        if not value:
            continue
        if value.startswith("evidence/security/"):
            value = value.removeprefix("evidence/security/")
        out.append(value)
    return sorted(set(out))


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    sec = evidence_root() / "security"
    required = _parse_required(os.environ.get("GLYPHSER_MANDATORY_SECURITY_UPLOADS", ""))

    checklist: list[dict[str, Any]] = []
    for rel in required:
        path = sec / rel
        entry = {
            "artifact": rel,
            "exists": path.exists(),
            "readable": False,
            "json_parsed": None,
            "status": "FAIL",
        }
        if not path.exists():
            findings.append(f"missing_mandatory_upload:{rel}")
            checklist.append(entry)
            continue
        try:
            payload = path.read_text(encoding="utf-8")
            entry["readable"] = True
            if rel.endswith(".json"):
                json.loads(payload)
                entry["json_parsed"] = True
            entry["status"] = "PASS"
        except Exception:
            if rel.endswith(".json"):
                findings.append(f"unreadable_or_invalid_json_artifact:{rel}")
            else:
                findings.append(f"unreadable_artifact:{rel}")
        checklist.append(entry)

    artifact = {
        "status": "PASS" if not findings else "FAIL",
        "required_artifacts": required,
        "checklist": checklist,
    }
    artifact_path = sec / "post_release_verification_checklist_artifact.json"
    write_json_report(artifact_path, artifact)

    sig_path = artifact_path.with_suffix(".json.sig")
    sig = sign_file(artifact_path, key=current_key(strict=False))
    sig_path.write_text(sig + "\n", encoding="utf-8")
    if not verify_file(artifact_path, sig, key=current_key(strict=False)):
        findings.append("post_release_verification_checklist_artifact_signature_invalid")

    gate = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "required_count": len(required),
            "retrievable_count": sum(1 for item in checklist if item.get("status") == "PASS"),
        },
        "metadata": {"gate": "post_release_verification_checklist_artifact"},
    }
    out = sec / "post_release_verification_checklist_artifact_gate.json"
    write_json_report(out, gate)
    print(f"POST_RELEASE_VERIFICATION_CHECKLIST_ARTIFACT: {gate['status']}")
    print(f"Artifact: {artifact_path}")
    print(f"Gate: {out}")
    return 0 if gate["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
