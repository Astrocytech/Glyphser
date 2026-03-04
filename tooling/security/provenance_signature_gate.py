#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.glyphser.security.artifact_signing import current_key, key_metadata, verify_file
from tooling.lib.path_config import evidence_root


def _verify_pair(path: Path, sig_path: Path, *, strict_key: bool) -> tuple[bool, str]:
    if not path.exists():
        return False, "missing_artifact"
    if not sig_path.exists():
        return False, "missing_signature"
    sig = sig_path.read_text(encoding="utf-8").strip()
    if not sig:
        return False, "empty_signature"
    if not verify_file(path, sig, key=current_key(strict=strict_key)):
        return False, "signature_mismatch"
    return True, "ok"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify signatures on security provenance artifacts.")
    parser.add_argument("--strict-key", action="store_true", help="Require GLYPHSER_PROVENANCE_HMAC_KEY.")
    args = parser.parse_args([] if argv is None else argv)

    sec = evidence_root() / "security"
    checks: dict[str, dict[str, str | bool]] = {}
    pairs = [
        ("sbom", sec / "sbom.json", sec / "sbom.json.sig"),
        ("build_provenance", sec / "build_provenance.json", sec / "build_provenance.json.sig"),
        ("slsa_provenance_v1", sec / "slsa_provenance_v1.json", sec / "slsa_provenance_v1.json.sig"),
    ]
    ok_all = True
    for name, path, sig_path in pairs:
        try:
            ok, reason = _verify_pair(path, sig_path, strict_key=args.strict_key)
        except ValueError as exc:
            ok, reason = False, str(exc)
        checks[name] = {
            "ok": ok,
            "reason": reason,
            "artifact": str(path.relative_to(ROOT)).replace("\\", "/"),
            "signature": str(sig_path.relative_to(ROOT)).replace("\\", "/"),
        }
        if not ok:
            ok_all = False

    payload: dict[str, object] = {
        "status": "PASS" if ok_all else "FAIL",
        "checks": checks,
        "metadata": {"key_provenance": key_metadata(strict=args.strict_key), "gate": "provenance_signature_gate"},
    }
    out = sec / "provenance_signature.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PROVENANCE_SIGNATURE_GATE: {payload['status']}")
    print(f"Report: {out}")
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
