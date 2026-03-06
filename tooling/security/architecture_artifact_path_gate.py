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

ARCH_DOCS = (
    ROOT / "docs" / "ARCHITECTURE.md",
    ROOT / "governance" / "security" / "SECURITY_ARCHITECTURE.md",
    ROOT / "governance" / "security" / "EVIDENCE_FLOW_ARCHITECTURE.md",
)
WORKFLOWS = (
    ROOT / ".github" / "workflows" / "ci.yml",
    ROOT / ".github" / "workflows" / "security-maintenance.yml",
    ROOT / ".github" / "workflows" / "release.yml",
)

DOC_REF_RE = re.compile(r"`(?P<ref>[A-Za-z0-9_./<>\-*]+(?:\.json(?:\.sig)?))`")
WF_ARTIFACT_RE = re.compile(r"security/(?P<name>[A-Za-z0-9_.-]+(?:\.json(?:\.sig)?))")


def _doc_artifact_refs(path: Path) -> set[str]:
    refs: set[str] = set()
    for match in DOC_REF_RE.finditer(path.read_text(encoding="utf-8")):
        ref = match.group("ref").strip()
        if "<" in ref or ">" in ref or "*" in ref:
            continue
        refs.add(Path(ref).name)
    return refs


def _workflow_artifacts(path: Path) -> set[str]:
    out: set[str] = set()
    for match in WF_ARTIFACT_RE.finditer(path.read_text(encoding="utf-8")):
        out.add(match.group("name").strip())
    return out


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    referenced: set[str] = set()
    available: set[str] = set()

    for doc in ARCH_DOCS:
        if not doc.exists():
            findings.append(f"missing_architecture_doc:{doc}")
            continue
        referenced.update(_doc_artifact_refs(doc))

    for wf in WORKFLOWS:
        if not wf.exists():
            findings.append(f"missing_workflow:{wf}")
            continue
        available.update(_workflow_artifacts(wf))

    evidence_security = ROOT / "evidence" / "security"
    if evidence_security.exists():
        for artifact in evidence_security.glob("*.json*"):
            available.add(artifact.name)

    for item in sorted(referenced):
        if item not in available:
            findings.append(f"architecture_artifact_path_unmapped:{item}")

    if not referenced:
        findings.append("no_architecture_artifact_paths_found")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "architecture_docs_checked": len(ARCH_DOCS),
            "referenced_artifact_paths": len(referenced),
            "available_artifact_paths": len(available),
        },
        "metadata": {"gate": "architecture_artifact_path_gate"},
    }
    out = evidence_root() / "security" / "architecture_artifact_path_gate.json"
    write_json_report(out, report)
    print(f"ARCHITECTURE_ARTIFACT_PATH_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
