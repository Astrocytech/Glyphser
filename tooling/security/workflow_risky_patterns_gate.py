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

USES_RE = re.compile(r"^\s*(?:-\s*)?uses:\s*([^\s]+)\s*$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
UNTRUSTED_EXPR_RE = re.compile(r"\$\{\{\s*github\.event\.pull_request\.(?:title|body|head\.ref)\s*\}\}")
RUN_LINE_RE = re.compile(r"^\s*(?:-\s*)?run:\s*")


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    scanned = 0
    for wf in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        scanned += 1
        rel = str(wf.relative_to(ROOT)).replace("\\", "/")
        for idx, line in enumerate(wf.read_text(encoding="utf-8").splitlines(), start=1):
            if "permissions: write-all" in line:
                findings.append(f"forbidden_permission_write_all:{rel}:{idx}")
            uses_match = USES_RE.match(line)
            if uses_match:
                uses_ref = uses_match.group(1)
                if uses_ref.startswith("./"):
                    continue
                if "@" not in uses_ref:
                    findings.append(f"unpinned_action_ref:{rel}:{idx}:{uses_ref}")
                else:
                    _action, ref = uses_ref.rsplit("@", 1)
                    if not SHA_RE.fullmatch(ref):
                        findings.append(f"unpinned_action_ref:{rel}:{idx}:{uses_ref}")
            if RUN_LINE_RE.match(line) and UNTRUSTED_EXPR_RE.search(line):
                findings.append(f"untrusted_pr_expr_in_run:{rel}:{idx}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"scanned_workflows": scanned, "finding_count": len(findings)},
        "metadata": {"gate": "workflow_risky_patterns_gate"},
    }
    out = evidence_root() / "security" / "workflow_risky_patterns_gate.json"
    write_json_report(out, report)
    print(f"WORKFLOW_RISKY_PATTERNS_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
