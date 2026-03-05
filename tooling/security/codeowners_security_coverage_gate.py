#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY = ROOT / "governance" / "security" / "review_policy.json"
CODEOWNERS = ROOT / ".github" / "CODEOWNERS"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _codeowner_patterns(path: Path) -> set[str]:
    patterns: set[str] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if parts:
            patterns.add(parts[0])
    return patterns


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not POLICY.exists():
        findings.append("missing_review_policy")
        required: list[str] = []
    else:
        policy = _load_json(POLICY)
        raw = policy.get("required_codeowners_paths", []) if isinstance(policy, dict) else []
        required = [str(item).strip() for item in raw if isinstance(item, str) and str(item).strip()]

    if not CODEOWNERS.exists():
        findings.append("missing_codeowners")
        patterns: set[str] = set()
    else:
        patterns = _codeowner_patterns(CODEOWNERS)

    for critical_path in required:
        if critical_path not in patterns:
            findings.append(f"missing_codeowners_coverage:{critical_path}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "required_critical_paths": len(required),
            "codeowners_patterns": len(patterns),
            "covered_critical_paths": len(required) - sum(1 for x in findings if x.startswith("missing_codeowners_coverage:")),
        },
        "metadata": {"gate": "codeowners_security_coverage_gate"},
    }
    out = evidence_root() / "security" / "codeowners_security_coverage_gate.json"
    write_json_report(out, report)
    print(f"CODEOWNERS_SECURITY_COVERAGE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
