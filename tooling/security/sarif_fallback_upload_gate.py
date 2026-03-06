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

CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"
STEP_START_RE = re.compile(r"^\s*-\s+(?:name|uses):")
STEP_NAME_RE = re.compile(r"^\s*-\s+name:\s*(?P<name>.+?)\s*$")
IF_RE = re.compile(r"^\s*if:\s*(?P<if_expr>.+?)\s*$")
UPLOAD_SARIF_RE = re.compile(r"uses:\s*github/codeql-action/upload-sarif@")
FALLBACK_UPLOAD_NAME = "Upload security artifacts"
PUSH_ONLY_GUARDS = (
    "github.event_name == 'push'",
    'github.event_name == "push"',
)
FORK_SKIP_GUARD = "github.event_name != 'pull_request' || github.event.pull_request.head.repo.fork == false"


def _iter_steps(lines: list[str]) -> list[tuple[int, int]]:
    starts = [idx for idx, line in enumerate(lines) if STEP_START_RE.match(line)]
    if not starts:
        return []
    pairs: list[tuple[int, int]] = []
    for idx, start in enumerate(starts):
        end = starts[idx + 1] if idx + 1 < len(starts) else len(lines)
        pairs.append((start, end))
    return pairs


def _step_name(step_lines: list[str]) -> str:
    for line in step_lines:
        match = STEP_NAME_RE.match(line)
        if match:
            return match.group("name").strip()
    return "<unnamed-step>"


def _step_if(step_lines: list[str]) -> str:
    for line in step_lines:
        match = IF_RE.match(line)
        if match:
            return match.group("if_expr").strip()
    return ""


def _is_push_only(condition: str) -> bool:
    return any(guard in condition for guard in PUSH_ONLY_GUARDS)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not CI_WORKFLOW.exists():
        findings.append("missing_ci_workflow")
        report = {
            "status": "FAIL",
            "findings": findings,
            "summary": {"code_scanning_upload_steps": 0, "fallback_upload_steps": 0},
            "metadata": {"gate": "sarif_fallback_upload_gate"},
            "simulation_cases": [],
        }
        out = evidence_root() / "security" / "sarif_fallback_upload_gate.json"
        write_json_report(out, report)
        print(f"SARIF_FALLBACK_UPLOAD_GATE: {report['status']}")
        print(f"Report: {out}")
        return 1

    lines = CI_WORKFLOW.read_text(encoding="utf-8").splitlines()
    code_scanning_steps = 0
    fallback_steps = 0

    for start, end in _iter_steps(lines):
        step_lines = lines[start:end]
        step_text = "\n".join(step_lines)
        name = _step_name(step_lines)
        condition = _step_if(step_lines)

        if UPLOAD_SARIF_RE.search(step_text):
            code_scanning_steps += 1
            if not condition:
                findings.append(f"missing_code_scanning_skip_guard:{name}")
            elif not (_is_push_only(condition) or FORK_SKIP_GUARD in condition):
                findings.append(f"unexpected_code_scanning_skip_guard:{name}:{condition}")

        if name == FALLBACK_UPLOAD_NAME:
            fallback_steps += 1
            if condition and _is_push_only(condition):
                findings.append(f"fallback_upload_not_available_on_pull_request:{name}:{condition}")

    if code_scanning_steps == 0:
        findings.append("missing_code_scanning_upload_step")
    if fallback_steps == 0:
        findings.append("missing_fallback_upload_step")

    simulation_cases = [
        {"event_name": "pull_request", "is_fork": True, "expected_code_scanning_upload": False, "expected_fallback_upload": True},
        {"event_name": "pull_request", "is_fork": False, "expected_code_scanning_upload": False, "expected_fallback_upload": True},
        {"event_name": "push", "is_fork": False, "expected_code_scanning_upload": True, "expected_fallback_upload": True},
    ]
    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"code_scanning_upload_steps": code_scanning_steps, "fallback_upload_steps": fallback_steps},
        "metadata": {"gate": "sarif_fallback_upload_gate"},
        "simulation_cases": simulation_cases,
    }
    out = evidence_root() / "security" / "sarif_fallback_upload_gate.json"
    write_json_report(out, report)
    print(f"SARIF_FALLBACK_UPLOAD_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
