#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root
from tooling.security.report_io import write_json_report

WORKFLOWS = ROOT / ".github" / "workflows"
POLICY = ROOT / "governance" / "security" / "security_artifact_signature_policy.json"


def _extract_required_pairs(payload: dict[str, Any]) -> tuple[list[tuple[str, str]], list[str]]:
    findings: list[str] = []
    out: list[tuple[str, str]] = []
    raw = payload.get("required_signature_pairs", [])
    if not isinstance(raw, list):
        return out, ["invalid_required_signature_pairs"]
    for item in raw:
        if not isinstance(item, dict):
            findings.append("invalid_signature_pair_entry")
            continue
        artifact = str(item.get("artifact", "")).strip()
        signature = str(item.get("signature", "")).strip()
        if not artifact or not signature:
            findings.append("missing_signature_pair_fields")
            continue
        out.append((artifact, signature))
    return out, findings


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    scanned = 0
    workflows_with_uploads = 0
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    if not isinstance(policy, dict):
        raise ValueError("invalid security artifact signature policy")
    required_pairs, policy_findings = _extract_required_pairs(policy)
    findings.extend(policy_findings)

    for path in sorted(WORKFLOWS.glob("*.yml")):
        scanned += 1
        text = path.read_text(encoding="utf-8")
        if "upload-artifact@" not in text:
            continue
        workflows_with_uploads += 1
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        for artifact, signature in required_pairs:
            if artifact in text and signature not in text:
                findings.append(f"missing_signature_upload:{rel}:{artifact}:{signature}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "scanned_workflows": scanned,
            "workflows_with_upload_artifact": workflows_with_uploads,
            "required_signature_pairs": len(required_pairs),
        },
        "metadata": {"gate": "security_artifact_signature_coverage_gate"},
    }
    out = evidence_root() / "security" / "security_artifact_signature_coverage_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_ARTIFACT_SIGNATURE_COVERAGE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
