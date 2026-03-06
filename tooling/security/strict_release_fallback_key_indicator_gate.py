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

FALLBACK_POLICY = ROOT / "governance" / "security" / "fallback_secret_usage_policy.json"
RELEASE_WORKFLOW = ROOT / ".github" / "workflows" / "release.yml"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"invalid json object: {path}")
    return payload


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    policy = _load_json(FALLBACK_POLICY)
    fallback_literal = str(policy.get("fallback_literal", "")).strip()
    if not fallback_literal:
        raise ValueError("fallback_literal must be configured")

    release_text = RELEASE_WORKFLOW.read_text(encoding="utf-8")
    if fallback_literal in release_text:
        findings.append("release_workflow_contains_fallback_key_literal")

    key_report_path = evidence_root() / "security" / "key_provenance_continuity_gate.json"
    if not key_report_path.exists():
        findings.append("missing_key_provenance_continuity_report")
        fallback_sources: list[str] = []
    else:
        key_report = _load_json(key_report_path)
        gate_findings = key_report.get("findings", []) if isinstance(key_report, dict) else []
        fallback_sources = []
        if isinstance(gate_findings, list):
            for item in gate_findings:
                text = str(item)
                if text.startswith("fallback_signing_used:"):
                    sources = [part for part in text.split(":", 1)[1].split(",") if part]
                    fallback_sources.extend(sources)
        if fallback_sources:
            findings.append(f"fallback_signing_indicator_in_release_lane:{','.join(sorted(set(fallback_sources)))}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "release_workflow": str(RELEASE_WORKFLOW.relative_to(ROOT)).replace("\\", "/"),
            "fallback_literal_configured": bool(fallback_literal),
            "fallback_sources": sorted(set(fallback_sources)),
            "key_provenance_report_path": str(key_report_path.relative_to(ROOT)).replace("\\", "/"),
        },
        "metadata": {"gate": "strict_release_fallback_key_indicator_gate"},
    }
    out = evidence_root() / "security" / "strict_release_fallback_key_indicator_gate.json"
    write_json_report(out, report)
    print(f"STRICT_RELEASE_FALLBACK_KEY_INDICATOR_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
