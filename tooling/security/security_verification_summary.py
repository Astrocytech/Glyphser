#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.glyphser.security.artifact_signing import current_key, key_metadata, sign_file
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build signed security verification summary for auditors.")
    parser.add_argument("--strict-key", action="store_true", help="Require strict key for summary signature.")
    args = parser.parse_args([] if argv is None else argv)

    sec = evidence_root() / "security"
    required = {
        "policy_signature": sec / "policy_signature.json",
        "provenance_signature": sec / "provenance_signature.json",
        "evidence_attestation_gate": sec / "evidence_attestation_gate.json",
        "key_provenance_continuity_gate": sec / "key_provenance_continuity_gate.json",
        "signature_algorithm_policy_gate": sec / "signature_algorithm_policy_gate.json",
        "security_unsigned_json_gate": sec / "security_unsigned_json_gate.json",
    }
    checks: dict[str, dict[str, Any]] = {}
    findings: list[str] = []
    for name, path in required.items():
        payload = _load(path)
        status = str(payload.get("status", "MISSING")).upper()
        checks[name] = {"status": status, "path": str(path.relative_to(ROOT)).replace("\\", "/")}
        if status != "PASS":
            findings.append(f"non_pass_required_verification:{name}:{status}")

    summary = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "checks": checks,
        "metadata": {
            "gate": "security_verification_summary",
            "key_provenance": key_metadata(strict=args.strict_key),
        },
    }
    out = sec / "security_verification_summary.json"
    write_json_report(out, summary)
    sig = sec / "security_verification_summary.json.sig"
    sig.write_text(sign_file(out, key=current_key(strict=args.strict_key)) + "\n", encoding="utf-8")
    print(f"SECURITY_VERIFICATION_SUMMARY: {summary['status']}")
    print(f"Report: {out}")
    print(f"Signature: {sig}")
    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
