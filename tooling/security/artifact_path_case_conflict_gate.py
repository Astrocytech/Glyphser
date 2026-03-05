#!/usr/bin/env python3
from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

WORKFLOWS = ROOT / ".github" / "workflows"
EVIDENCE_SECURITY = ROOT / "evidence" / "security"
_PATH_RE = re.compile(r"\bsecurity/[A-Za-z0-9_.\-/]+")


def _normalized_key(path: str) -> str:
    return path.replace("\\", "/").lower()


def _collect_workflow_security_paths() -> dict[str, set[str]]:
    seen: dict[str, set[str]] = {}
    for wf in sorted(WORKFLOWS.glob("*.yml")):
        text = wf.read_text(encoding="utf-8")
        for match in _PATH_RE.finditer(text):
            rel = match.group(0)
            key = _normalized_key(rel)
            seen.setdefault(key, set()).add(f"{wf.name}:{rel}")
    return seen


def _collect_evidence_paths() -> dict[str, set[str]]:
    seen: dict[str, set[str]] = {}
    if not EVIDENCE_SECURITY.exists():
        return seen
    for path in EVIDENCE_SECURITY.rglob("*"):
        if not path.is_file():
            continue
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        key = _normalized_key(rel)
        seen.setdefault(key, set()).add(rel)
    return seen


def _conflicts(seen: dict[str, set[str]]) -> list[list[str]]:
    out: list[list[str]] = []
    for values in seen.values():
        if len(values) > 1:
            out.append(sorted(values))
    return sorted(out)


def _format_conflicts(prefix: str, groups: Iterable[list[str]]) -> list[str]:
    findings: list[str] = []
    for group in groups:
        findings.append(f"{prefix}:{'|'.join(group)}")
    return findings


def main(argv: list[str] | None = None) -> int:
    _ = argv
    workflow_seen = _collect_workflow_security_paths()
    evidence_seen = _collect_evidence_paths()

    workflow_conflicts = _conflicts(workflow_seen)
    evidence_conflicts = _conflicts(evidence_seen)

    findings = _format_conflicts("workflow_case_conflict", workflow_conflicts)
    findings.extend(_format_conflicts("evidence_case_conflict", evidence_conflicts))

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "workflow_paths_scanned": sum(len(v) for v in workflow_seen.values()),
            "evidence_paths_scanned": sum(len(v) for v in evidence_seen.values()),
            "workflow_conflicts": len(workflow_conflicts),
            "evidence_conflicts": len(evidence_conflicts),
        },
        "metadata": {"gate": "artifact_path_case_conflict_gate"},
    }
    out = evidence_root() / "security" / "artifact_path_case_conflict_gate.json"
    write_json_report(out, report)
    print(f"ARTIFACT_PATH_CASE_CONFLICT_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
