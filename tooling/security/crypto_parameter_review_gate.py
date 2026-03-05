#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root
from tooling.security.report_io import write_json_report

POLICY = ROOT / "governance" / "security" / "crypto_parameter_policy.json"
FORBIDDEN_HASHES = {"md5", "sha1"}


def _parse_utc(value: str) -> datetime | None:
    raw = value.strip()
    if not raw:
        return None
    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        dt = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    payload = json.loads(POLICY.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("crypto parameter policy must be a JSON object")

    min_key_bytes = int(payload.get("min_hmac_key_bytes", 0))
    allowed = {str(x).strip().lower() for x in payload.get("allowed_hash_algorithms", []) if str(x).strip()}
    forbidden = {str(x).strip().lower() for x in payload.get("forbidden_hash_algorithms", []) if str(x).strip()}
    review_max_age_days = int(payload.get("review_max_age_days", 0))
    reviewed_at = _parse_utc(str(payload.get("last_reviewed_utc", "")))

    if min_key_bytes < 32:
        findings.append("min_hmac_key_bytes_below_threshold")
    if FORBIDDEN_HASHES & allowed:
        findings.append(f"weak_hash_allowlisted:{','.join(sorted(FORBIDDEN_HASHES & allowed))}")
    if not FORBIDDEN_HASHES.issubset(forbidden):
        findings.append("weak_hashes_not_fully_forbidden")
    if review_max_age_days <= 0:
        findings.append("invalid_review_max_age_days")
    if reviewed_at is None:
        findings.append("invalid_last_reviewed_utc")
        review_age_days = -1
    else:
        now = datetime.now(timezone.utc)
        review_age_days = (now - reviewed_at).days
        if review_age_days > review_max_age_days:
            findings.append(f"crypto_parameter_review_stale:{review_age_days}>{review_max_age_days}")

    env_key = os.environ.get("GLYPHSER_PROVENANCE_HMAC_KEY", "")
    if env_key and len(env_key.encode("utf-8")) < min_key_bytes:
        findings.append("runtime_hmac_key_below_policy_minimum")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "min_hmac_key_bytes": min_key_bytes,
            "allowed_hash_algorithms": sorted(allowed),
            "forbidden_hash_algorithms": sorted(forbidden),
            "review_max_age_days": review_max_age_days,
            "review_age_days": review_age_days,
        },
        "metadata": {"gate": "crypto_parameter_review_gate"},
    }
    out = evidence_root() / "security" / "crypto_parameter_review_gate.json"
    write_json_report(out, report)
    print(f"CRYPTO_PARAMETER_REVIEW_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
