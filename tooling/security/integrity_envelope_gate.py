#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.glyphser.security.artifact_signing import current_key, sign_file, verify_file
from tooling.lib.path_config import evidence_root
from tooling.security.report_io import write_json_report

ENVELOPE = "security_integrity_envelope.json"
ENVELOPE_SIG = "security_integrity_envelope.json.sig"
LINKED_REPORTS = [
    "policy_signature.json",
    "provenance_signature.json",
    "evidence_attestation_index.json",
]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build and verify signed integrity envelope for core security attestations.")
    parser.add_argument("--strict-key", action="store_true")
    args = parser.parse_args([] if argv is None else argv)

    sec = evidence_root() / "security"
    sec.mkdir(parents=True, exist_ok=True)
    findings: list[str] = []
    links: dict[str, dict[str, str]] = {}

    for name in LINKED_REPORTS:
        path = sec / name
        if not path.exists():
            findings.append(f"missing_linked_report:{name}")
            continue
        links[name] = {"sha256": _sha(path)}

    envelope_path = sec / ENVELOPE
    sig_path = sec / ENVELOPE_SIG
    if not findings:
        payload = {"status": "PASS", "links": links}
        envelope_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        sig_path.write_text(sign_file(envelope_path, key=current_key(strict=args.strict_key)) + "\n", encoding="utf-8")
        sig = sig_path.read_text(encoding="utf-8").strip()
        if not sig or not verify_file(envelope_path, sig, key=current_key(strict=args.strict_key)):
            findings.append("integrity_envelope_signature_invalid")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "linked_reports": LINKED_REPORTS,
            "envelope_path": str((sec / ENVELOPE).relative_to(ROOT)).replace("\\", "/"),
        },
        "metadata": {"gate": "integrity_envelope_gate", "strict_key": args.strict_key},
    }
    out = sec / "integrity_envelope_gate.json"
    write_json_report(out, report)
    print(f"INTEGRITY_ENVELOPE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
