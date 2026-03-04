#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from runtime.glyphser.security.artifact_signing import sign_bytes
from tooling.lib.path_config import evidence_root

ROOT = Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    _ = argv
    payload = b"glyphser-crypto-agility"
    findings: list[str] = []

    k1 = b"stage-s-key-a"
    k2 = b"stage-s-key-b"
    sig1 = sign_bytes(payload, key=k1)
    sig2 = sign_bytes(payload, key=k2)
    if sig1 == sig2:
        findings.append("key_rollover_not_distinguishable")

    repeat = sign_bytes(payload, key=k1)
    if repeat != sig1:
        findings.append("non_deterministic_signature")

    matrix = {
        "hmac_sha256_current_key": {"status": "PASS" if sig1 else "FAIL"},
        "hmac_sha256_next_key": {"status": "PASS" if sig2 else "FAIL"},
        "rollover_distinctness": {"status": "PASS" if sig1 != sig2 else "FAIL"},
        "deterministic_repeatability": {"status": "PASS" if repeat == sig1 else "FAIL"},
    }

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"matrix": matrix},
        "metadata": {"gate": "crypto_agility_matrix_gate"},
    }
    out = evidence_root() / "security" / "crypto_agility_matrix_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CRYPTO_AGILITY_MATRIX_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
