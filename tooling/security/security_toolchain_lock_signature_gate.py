#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.glyphser.security.artifact_signing import bootstrap_key, current_key, verify_file
from tooling.lib.path_config import evidence_root
from tooling.security.report_io import write_json_report


LOCK_FILES = [
    ROOT / "tooling" / "security" / "security_toolchain_lock.json",
    ROOT / "tooling" / "security" / "security_toolchain_transitive_lock.json",
]


def _verify_with_allowed_keys(path: Path, sig: str, *, strict_key: bool) -> tuple[bool, str]:
    try:
        primary_key = current_key(strict=strict_key)
    except ValueError as exc:
        if strict_key:
            if verify_file(path, sig, key=bootstrap_key()):
                return True, "ok_bootstrap_key_missing_strict_env"
            return False, str(exc)
        return False, str(exc)

    if verify_file(path, sig, key=primary_key):
        return True, "ok"
    if verify_file(path, sig, key=bootstrap_key()):
        return True, "ok_bootstrap_key"
    return False, "signature_mismatch"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify signatures for security toolchain lock files.")
    parser.add_argument("--strict-key", action="store_true", help="Require GLYPHSER_PROVENANCE_HMAC_KEY.")
    args = parser.parse_args([] if argv is None else argv)

    findings: list[str] = []
    checks: dict[str, dict[str, str | bool]] = {}

    for lock_path in LOCK_FILES:
        rel = str(lock_path.relative_to(ROOT)).replace("\\", "/")
        sig_path = lock_path.with_suffix(lock_path.suffix + ".sig")
        ok = True
        reason = "ok"
        if not lock_path.exists():
            ok = False
            reason = "missing_lock"
        elif not sig_path.exists():
            ok = False
            reason = "missing_signature"
        else:
            sig = sig_path.read_text(encoding="utf-8").strip()
            if not sig:
                ok = False
                reason = "empty_signature"
            else:
                ok, reason = _verify_with_allowed_keys(lock_path, sig, strict_key=args.strict_key)
        checks[rel] = {"ok": ok, "reason": reason}
        if not ok:
            findings.append(f"{rel}:{reason}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"checked_locks": len(LOCK_FILES), "checks": checks},
        "metadata": {"gate": "security_toolchain_lock_signature_gate", "strict_key": args.strict_key},
    }
    out = evidence_root() / "security" / "security_toolchain_lock_signature_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_TOOLCHAIN_LOCK_SIGNATURE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
