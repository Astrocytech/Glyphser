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
ROOT_ASSIGN_RE = re.compile(r"GLYPHSER_EVIDENCE_ROOT:\s*([^\n]+)")
REQUIRED_PREFIX = "evidence/runs/${{ github.run_id }}/release-"
FORBIDDEN_ROOT_TOKENS = ("security-maintenance", "security-super-extended", "/ci", "security-matrix")


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not RELEASE_WORKFLOW.exists():
        findings.append("missing_release_workflow:.github/workflows/release.yml")
        roots: list[str] = []
    else:
        text = RELEASE_WORKFLOW.read_text(encoding="utf-8")
        roots = [match.group(1).strip().strip("'\"") for match in ROOT_ASSIGN_RE.finditer(text)]
        if not roots:
            findings.append("no_release_evidence_roots_declared")
        for value in roots:
            if not value.startswith(REQUIRED_PREFIX):
                findings.append(f"non_release_evidence_root:{value}")
            if any(token in value for token in FORBIDDEN_ROOT_TOKENS):
                findings.append(f"release_evidence_root_not_isolated:{value}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "release_workflow": str(RELEASE_WORKFLOW.relative_to(ROOT)).replace("\\", "/"),
            "declared_release_evidence_roots": roots,
            "required_prefix": REQUIRED_PREFIX,
            "forbidden_tokens": list(FORBIDDEN_ROOT_TOKENS),
        },
        "metadata": {"gate": "release_evidence_root_isolation_gate"},
    }
    out = evidence_root() / "security" / "release_evidence_root_isolation_gate.json"
    write_json_report(out, report)
    print(f"RELEASE_EVIDENCE_ROOT_ISOLATION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
