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

WORKFLOWS = (
    ".github/workflows/ci.yml",
    ".github/workflows/security-maintenance.yml",
)
STEP_START_RE = re.compile(r"^\s*-\s+(?:name|uses):")
UPLOAD_SARIF_RE = re.compile(r"uses:\s*github/codeql-action/upload-sarif@")
STEP_NAME_RE = re.compile(r"^\s*-\s+name:\s*(?P<name>.+?)\s*$")
SARIF_FILE_RE = re.compile(r"^\s*sarif_file:\s*(?P<sarif_file>\S+)\s*$")


def _iter_steps(lines: list[str]) -> list[tuple[int, int]]:
    starts = [idx for idx, line in enumerate(lines) if STEP_START_RE.match(line)]
    if not starts:
        return []
    steps: list[tuple[int, int]] = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(lines)
        steps.append((start, end))
    return steps


def _step_name(step_lines: list[str]) -> str:
    for line in step_lines:
        match = STEP_NAME_RE.match(line)
        if match:
            return match.group("name").strip()
    return "<unnamed-step>"


def _sarif_file(step_lines: list[str]) -> str:
    for line in step_lines:
        match = SARIF_FILE_RE.match(line)
        if match:
            return match.group("sarif_file").strip()
    return ""


def _has_prior_producer(prefix: str, sarif_file: str) -> bool:
    escaped = re.escape(sarif_file)
    producer_patterns = (
        rf"(?:--output|-o)\s+{escaped}(?:\s|$)",
        rf">\s*{escaped}(?:\s|$)",
        rf"tee\s+{escaped}(?:\s|$)",
    )
    return any(re.search(pattern, prefix) for pattern in producer_patterns)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    upload_steps_checked = 0
    workflows_checked = 0

    for rel in WORKFLOWS:
        workflow = ROOT / rel
        if not workflow.exists():
            findings.append(f"missing_workflow:{rel}")
            continue
        workflows_checked += 1
        lines = workflow.read_text(encoding="utf-8").splitlines()
        for start, end in _iter_steps(lines):
            step_lines = lines[start:end]
            step_text = "\n".join(step_lines)
            if not UPLOAD_SARIF_RE.search(step_text):
                continue
            upload_steps_checked += 1
            step_name = _step_name(step_lines)
            sarif_file = _sarif_file(step_lines)
            if not sarif_file:
                findings.append(f"missing_sarif_file_input:{rel}:{step_name}")
                continue
            prefix = "\n".join(lines[:start])
            if not _has_prior_producer(prefix, sarif_file):
                findings.append(f"missing_prior_sarif_output:{rel}:{step_name}:{sarif_file}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "workflows_checked": workflows_checked,
            "required_workflows": len(WORKFLOWS),
            "upload_steps_checked": upload_steps_checked,
        },
        "metadata": {"gate": "sarif_upload_prerequisite_gate"},
    }
    out = evidence_root() / "security" / "sarif_upload_prerequisite_gate.json"
    write_json_report(out, report)
    print(f"SARIF_UPLOAD_PREREQUISITE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
