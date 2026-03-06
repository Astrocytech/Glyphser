#!/usr/bin/env python3
from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

RELEASE_WORKFLOW = ROOT / ".github" / "workflows" / "release.yml"
NEEDS_RE = re.compile(r"^\s*publish-pypi:\s*$[\s\S]*?^\s*needs:\s*\[([^\]]+)\]", re.MULTILINE)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not RELEASE_WORKFLOW.exists():
        findings.append("missing_release_workflow:.github/workflows/release.yml")
        text = ""
    else:
        text = RELEASE_WORKFLOW.read_text(encoding="utf-8")

    publish_needs: list[str] = []
    match = NEEDS_RE.search(text)
    if not match:
        findings.append("publish_job_missing_needs_dependency")
    else:
        publish_needs = [token.strip() for token in match.group(1).split(",") if token.strip()]
        if "verify-signatures" not in publish_needs:
            findings.append("publish_job_not_blocked_by_verify_signatures")

    verify_has_rollback = "python tooling/security/release_rollback_provenance_gate.py" in text
    if not verify_has_rollback:
        findings.append("verify_signatures_missing_release_rollback_provenance_gate")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "publish_needs": publish_needs,
            "verify_contains_release_rollback_gate": verify_has_rollback,
        },
        "metadata": {"gate": "release_publish_rollback_order_gate"},
    }
    out = evidence_root() / "security" / "release_publish_rollback_order_gate.json"
    write_json_report(out, report)
    print(f"RELEASE_PUBLISH_ROLLBACK_ORDER_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
