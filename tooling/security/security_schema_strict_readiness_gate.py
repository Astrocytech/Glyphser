#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root
from tooling.security.advanced_policy import load_policy
from tooling.security.report_io import write_json_report


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    strict_enabled = os.environ.get("GLYPHSER_SECURITY_SCHEMA_STRICT", "").strip().lower() in {"1", "true", "yes", "on"}
    policy = load_policy()
    threshold = float(policy.get("schema_strict_min_migration_pct", 95.0))
    report_path = evidence_root() / "security" / "security_schema_migration_tracker.json"
    tracker = _load(report_path)
    pct = float(_load(report_path).get("summary", {}).get("migration_pct", 0.0)) if tracker else 0.0
    findings: list[str] = []
    if not tracker:
        findings.append("missing_schema_migration_tracker_report")
    if strict_enabled and pct < threshold:
        findings.append(f"strict_mode_blocked_by_migration_pct:{pct:.2f}<{threshold:.2f}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "strict_enabled": strict_enabled,
            "migration_pct": pct,
            "required_migration_pct": threshold,
            "tracker_report": str(report_path.relative_to(ROOT)).replace("\\", "/"),
        },
        "metadata": {"gate": "security_schema_strict_readiness_gate"},
    }
    out = evidence_root() / "security" / "security_schema_strict_readiness_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_SCHEMA_STRICT_READINESS_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
