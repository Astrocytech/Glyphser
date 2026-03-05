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


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"invalid json object: {path}")
    return payload


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    policy = _load_json(ROOT / "governance" / "security" / "fallback_secret_usage_policy.json")
    fallback_literal = str(policy.get("fallback_literal", "")).strip()
    allowlisted = {str(x) for x in policy.get("allowlisted_workflows", []) if isinstance(x, str)}
    if not fallback_literal:
        raise ValueError("fallback_literal must be configured")

    workflows = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
    observed: list[str] = []
    for wf in workflows:
        rel = str(wf.relative_to(ROOT)).replace("\\", "/")
        text = wf.read_text(encoding="utf-8")
        if fallback_literal not in text:
            continue
        observed.append(rel)
        if rel not in allowlisted:
            findings.append(f"fallback_literal_not_allowlisted:{rel}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "fallback_literal": fallback_literal,
            "observed_workflows": observed,
            "allowlisted_workflows": sorted(allowlisted),
        },
        "metadata": {"gate": "fallback_secret_usage_gate"},
    }
    out = evidence_root() / "security" / "fallback_secret_usage_gate.json"
    write_json_report(out, report)
    print(f"FALLBACK_SECRET_USAGE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
