#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.glyphser.security.artifact_signing import current_key, verify_file
from tooling.lib.path_config import evidence_root


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
                try:
                    if not verify_file(policy_path, sig, key=current_key(strict=args.strict_key)):
                        ok = False
                        reason = "signature_mismatch"
                except ValueError as exc:
                    ok = False
                    reason = str(exc)
        checks[rel] = {"ok": ok, "reason": reason}
        if not ok:
            findings.append(f"{rel}: {reason}")

    payload = {"status": "PASS" if not findings else "FAIL", "checks": checks, "findings": findings}
    out = evidence_root() / "security" / "policy_signature.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"POLICY_SIGNATURE_GATE: {payload['status']}")
    print(f"Report: {out}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
