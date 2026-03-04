#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import math
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _entropy_bits(text: str) -> float:
    if not text:
        return 0.0
    counts: dict[str, int] = {}
    for ch in text:
        counts[ch] = counts.get(ch, 0) + 1
    total = float(len(text))
    entropy = 0.0
    for count in counts.values():
        p = count / total
        if p > 0.0:
            entropy -= p * math.log2(p)
    return entropy * len(text)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = json.loads((ROOT / "governance" / "security" / "key_management_policy.json").read_text(encoding="utf-8"))
    if not isinstance(policy, dict):
        raise ValueError("invalid key management policy")

    key_env = str(policy.get("signing_key_env", "GLYPHSER_PROVENANCE_HMAC_KEY"))
    rot_env = str(policy.get("rotation_timestamp_env", "GLYPHSER_PROVENANCE_KEY_ROTATED_AT"))
    min_len = int(policy.get("minimum_key_length", 32))
    min_entropy = float(policy.get("minimum_entropy_bits", 80))
    max_age = int(policy.get("maximum_rotation_age_days", 90))

    key = os.environ.get(key_env, "")
    rot = os.environ.get(rot_env, "")
    findings: list[str] = []
    summary: dict[str, Any] = {
        "key_env": key_env,
        "rotation_timestamp_env": rot_env,
        "minimum_key_length": min_len,
        "minimum_entropy_bits": min_entropy,
        "maximum_rotation_age_days": max_age,
    }

    if len(key) < min_len:
        findings.append("signing_key_below_min_length")
    entropy = _entropy_bits(key)
    summary["measured_entropy_bits"] = entropy
    if entropy < min_entropy:
        findings.append("signing_key_entropy_below_minimum")

    if not rot:
        findings.append("missing_key_rotation_timestamp")
    else:
        try:
            rotated = datetime.fromisoformat(rot.replace("Z", "+00:00"))
            if rotated.tzinfo is None:
                rotated = rotated.replace(tzinfo=UTC)
            age_days = (datetime.now(UTC) - rotated.astimezone(UTC)).days
            summary["rotation_age_days"] = age_days
            if age_days > max_age:
                findings.append("signing_key_rotation_too_old")
        except Exception:
            findings.append("invalid_key_rotation_timestamp")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": summary,
        "metadata": {"gate": "key_management"},
    }
    out = evidence_root() / "security" / "key_management.json"
    write_json_report(out, report)
    print(f"KEY_MANAGEMENT_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
