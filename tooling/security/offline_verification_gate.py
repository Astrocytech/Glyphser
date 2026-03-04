#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
bootstrap_key = artifact_signing.bootstrap_key
current_key = artifact_signing.current_key
verify_file = artifact_signing.verify_file
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
from tooling.security.evidence_chain_of_custody import verify_index
from tooling.security.report_io import write_json_report

MANIFEST = ROOT / "governance" / "security" / "policy_signature_manifest.json"


def _verify_policy_signatures() -> list[str]:
    findings: list[str] = []
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    policies = payload.get("policies", []) if isinstance(payload, dict) else []
    if not isinstance(policies, list):
        return ["invalid_policy_signature_manifest"]
    for rel in policies:
        if not isinstance(rel, str):
            findings.append("invalid_manifest_entry")
            continue
        path = ROOT / rel
        sig = path.with_suffix(path.suffix + ".sig")
        if not path.exists():
            findings.append(f"missing_policy:{rel}")
            continue
        if not sig.exists():
            findings.append(f"missing_policy_signature:{rel}")
            continue
        sig_text = sig.read_text(encoding="utf-8").strip()
        if not sig_text:
            findings.append(f"empty_policy_signature:{rel}")
            continue
        if verify_file(path, sig_text, key=current_key(strict=False)):
            continue
        if verify_file(path, sig_text, key=bootstrap_key()):
            continue
        findings.append(f"invalid_policy_signature:{rel}")
    return findings


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    if not MANIFEST.exists():
        findings.append("missing_policy_signature_manifest")
    else:
        findings.extend(_verify_policy_signatures())

    coc = verify_index(strict_key=False)
    if coc.get("status") != "PASS":
        for item in coc.get("findings", []):
            findings.append(f"chain_of_custody:{item}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "manifest_path": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"),
            "chain_of_custody_status": coc.get("status", "UNKNOWN"),
        },
        "metadata": {"gate": "offline_verification_gate", "network_access": "not_required"},
    }
    out = evidence_root() / "security" / "offline_verification_gate.json"
    write_json_report(out, report)
    print(f"OFFLINE_VERIFICATION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
