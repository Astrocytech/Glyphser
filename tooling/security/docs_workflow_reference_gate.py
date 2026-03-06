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

DOC_ROOTS = (ROOT / "governance" / "security", ROOT / "docs")
STEP_REF_RE = re.compile(r"(?P<wf>\.github/workflows/[A-Za-z0-9_.-]+\.yml)#step:(?P<step>[^\n`]+)")
STEP_NAME_RE = re.compile(r"^\s*-\s+name:\s*(?P<name>.+?)\s*$")


def _workflow_steps(path: Path) -> set[str]:
    steps: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        m = STEP_NAME_RE.match(line)
        if not m:
            continue
        name = m.group("name").strip()
        if name:
            steps.add(name)
    return steps


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    refs_checked = 0
    workflow_cache: dict[str, set[str]] = {}

    docs: list[Path] = []
    for root in DOC_ROOTS:
        if root.exists():
            docs.extend(sorted(root.rglob("*.md")))

    for doc in docs:
        rel_doc = str(doc.relative_to(ROOT)).replace("\\", "/")
        for match in STEP_REF_RE.finditer(doc.read_text(encoding="utf-8")):
            refs_checked += 1
            wf_rel = match.group("wf").strip()
            step = match.group("step").strip()
            wf_path = ROOT / wf_rel
            if not wf_path.exists():
                findings.append(f"missing_workflow_reference:{rel_doc}:{wf_rel}")
                continue
            if wf_rel not in workflow_cache:
                workflow_cache[wf_rel] = _workflow_steps(wf_path)
            if step not in workflow_cache[wf_rel]:
                findings.append(f"missing_workflow_step_reference:{rel_doc}:{wf_rel}:{step}")

    if refs_checked == 0:
        findings.append("no_workflow_step_references_found")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "docs_scanned": len(docs),
            "workflow_step_references_checked": refs_checked,
            "workflows_resolved": len(workflow_cache),
        },
        "metadata": {"gate": "docs_workflow_reference_gate"},
    }
    out = evidence_root() / "security" / "docs_workflow_reference_gate.json"
    write_json_report(out, report)
    print(f"DOCS_WORKFLOW_REFERENCE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
