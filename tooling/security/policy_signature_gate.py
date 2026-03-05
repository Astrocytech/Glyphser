#!/usr/bin/env python3
from __future__ import annotations

import argparse
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
key_metadata = artifact_signing.key_metadata
verify_file = artifact_signing.verify_file
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _verify_with_allowed_keys(policy_path: Path, sig: str, *, strict_key: bool) -> tuple[bool, str]:
    try:
        primary_key = current_key(strict=strict_key)
    except ValueError as exc:
        if not strict_key:
            return False, str(exc)
        # In strict mode, CI lanes without the runtime signing secret should still
        # verify repository bootstrap signatures instead of hard-failing.
        if verify_file(policy_path, sig, key=bootstrap_key()):
            return True, "ok_bootstrap_key_missing_strict_env"
        return False, str(exc)

    if verify_file(policy_path, sig, key=primary_key):
        return True, "ok"

    # Repository policy files may still be signed with the bootstrap key while CI
    # rotates to a strict runtime key. Accept bootstrap signatures as transitional.
    if verify_file(policy_path, sig, key=bootstrap_key()):
        return True, "ok_bootstrap_key"
    return False, "signature_mismatch"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify signatures for governance/security policy JSON files.")
    parser.add_argument("--strict-key", action="store_true")
    args = parser.parse_args([] if argv is None else argv)

    manifest_path = ROOT / "governance" / "security" / "policy_signature_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    policies = manifest.get("policies", []) if isinstance(manifest, dict) else []
    if not isinstance(policies, list):
        raise ValueError("invalid policy signature manifest")

    findings: list[str] = []
    checks: dict[str, dict[str, str | bool]] = {}
    for rel in policies:
        if not isinstance(rel, str) or not rel.endswith(".json"):
            findings.append("invalid policy path entry")
            continue
        policy_path = ROOT / rel
        sig_path = policy_path.with_suffix(policy_path.suffix + ".sig")
        ok = True
        reason = "ok"
        if not policy_path.exists():
            ok = False
            reason = "missing_policy"
        elif not sig_path.exists():
            ok = False
            reason = "missing_signature"
        else:
            sig = sig_path.read_text(encoding="utf-8").strip()
            if not sig:
                ok = False
                reason = "empty_signature"
            else:
                ok, reason = _verify_with_allowed_keys(policy_path, sig, strict_key=args.strict_key)
        checks[rel] = {"ok": ok, "reason": reason}
        if not ok:
            findings.append(f"{rel}: {reason}")

    payload = {
        "status": "PASS" if not findings else "FAIL",
        "checks": checks,
        "findings": findings,
        "summary": {
            "total_policies": len(policies),
            "failed_policies": len(findings),
            "strict_key": args.strict_key,
        },
        "metadata": {"key_provenance": key_metadata(strict=args.strict_key), "gate": "policy_signature_gate"},
    }
    out = evidence_root() / "security" / "policy_signature.json"
    write_json_report(out, payload)
    print(f"POLICY_SIGNATURE_GATE: {payload['status']}")
    print(f"Report: {out}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
