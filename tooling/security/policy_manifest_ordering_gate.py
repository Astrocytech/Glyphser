#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

MANIFEST = ROOT / "governance" / "security" / "policy_signature_manifest.json"


def _normalize_policy_entry(entry: str) -> str:
    return "/".join(part for part in entry.replace("\\", "/").strip().split("/") if part)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    policies = payload.get("policies", []) if isinstance(payload, dict) else []
    if not isinstance(policies, list):
        raise ValueError("invalid policy signature manifest")

    findings: list[str] = []
    checked: list[str] = []
    checked_normalized: list[str] = []
    for idx, policy in enumerate(policies):
        if not isinstance(policy, str):
            findings.append(f"non_string_policy_entry:{idx}")
            continue
        normalized = _normalize_policy_entry(policy)
        if not normalized:
            findings.append(f"empty_policy_entry:{idx}")
            continue
        checked.append(policy)
        checked_normalized.append(normalized)
        if policy != normalized:
            findings.append(f"non_canonical_policy_entry:{idx}")

    sorted_checked = sorted(checked_normalized)
    if checked_normalized != sorted_checked:
        findings.append("policy_manifest_not_sorted_lexicographically")
        for idx, (current, expected) in enumerate(zip(checked_normalized, sorted_checked)):
            if current != expected:
                findings.append(f"out_of_order_entry:{idx}:{current}!=expected:{expected}")
                break

    if len(set(checked_normalized)) != len(checked_normalized):
        findings.append("duplicate_policy_manifest_entries")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "manifest_entries": len(policies),
            "checked_entries": len(checked),
            "normalized_entries": len(checked_normalized),
        },
        "metadata": {"gate": "policy_manifest_ordering_gate"},
    }
    out = evidence_root() / "security" / "policy_manifest_ordering_gate.json"
    write_json_report(out, report)
    print(f"POLICY_MANIFEST_ORDERING_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
