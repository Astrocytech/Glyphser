#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from tooling.lib.path_config import evidence_root

ROOT = Path(__file__).resolve().parents[2]

TARGETS = [
    ROOT / "governance" / "security" / "policy_signature_manifest.json",
    ROOT / "governance" / "security" / "advanced_hardening_policy.json",
    ROOT / "evidence" / "security" / "build_provenance.json",
]


def _canon(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    checked: list[str] = []
    for path in TARGETS:
        if not path.exists():
            findings.append(f"missing_target:{path}")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        canon = _canon(data)
        reparsed = json.loads(canon)
        if _canon(reparsed) != canon:
            findings.append(f"roundtrip_mismatch:{path}")
        checked.append(str(path.relative_to(ROOT)).replace("\\", "/"))

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"checked": checked, "count": len(checked)},
        "metadata": {"gate": "canonical_json_roundtrip_gate"},
    }
    out = evidence_root() / "security" / "canonical_json_roundtrip_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CANONICAL_JSON_ROUNDTRIP_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
