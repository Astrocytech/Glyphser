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
    ".github/workflows/security-super-extended.yml",
)
STEP_START_RE = re.compile(r"^\s*-\s+(?:name|uses):")
STEP_NAME_RE = re.compile(r"^\s*-\s+name:\s*(?P<name>.+?)\s*$")
WILDCARD_RE = re.compile(r"[*?\[]")


def _iter_steps(lines: list[str]) -> list[tuple[int, int]]:
    starts = [idx for idx, line in enumerate(lines) if STEP_START_RE.match(line)]
    if not starts:
        return []
    steps: list[tuple[int, int]] = []
    for idx, start in enumerate(starts):
        end = starts[idx + 1] if idx + 1 < len(starts) else len(lines)
        steps.append((start, end))
    return steps


def _step_name(step_lines: list[str]) -> str:
    for line in step_lines:
        match = STEP_NAME_RE.match(line)
        if match:
            return match.group("name").strip()
    return "<unnamed-step>"


def _extract_upload_paths(step_lines: list[str]) -> list[str]:
    paths: list[str] = []
    in_multiline_path = False
    multiline_indent = 0
    for line in step_lines:
        stripped = line.strip()
        if in_multiline_path:
            current_indent = len(line) - len(line.lstrip(" "))
            if stripped and current_indent > multiline_indent:
                paths.append(stripped)
                continue
            in_multiline_path = False
        if stripped.startswith("path:"):
            prefix_indent = len(line) - len(line.lstrip(" "))
            value = stripped.split(":", 1)[1].strip()
            if value == "|" or value == ">":
                in_multiline_path = True
                multiline_indent = prefix_indent
                continue
            if value:
                paths.append(value)
    return paths


def _is_upload_artifact_step(step_lines: list[str]) -> bool:
    step_text = "\n".join(step_lines)
    return "uses: actions/upload-artifact@" in step_text


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
            if not _is_upload_artifact_step(step_lines):
                continue
            upload_steps_checked += 1
            step_name = _step_name(step_lines)
            for path in _extract_upload_paths(step_lines):
                if WILDCARD_RE.search(path):
                    findings.append(f"wildcard_upload_path:{rel}:{step_name}:{path}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "workflows_checked": workflows_checked,
            "required_workflows": len(WORKFLOWS),
            "upload_steps_checked": upload_steps_checked,
        },
        "metadata": {"gate": "workflow_upload_wildcard_gate"},
    }
    out = evidence_root() / "security" / "workflow_upload_wildcard_gate.json"
    write_json_report(out, report)
    print(f"WORKFLOW_UPLOAD_WILDCARD_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
