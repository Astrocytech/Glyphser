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

REQUIRED_EXPLICIT_PERMISSIONS = {
    "ci.yml",
    "security-maintenance.yml",
    "security-super-extended.yml",
    "release.yml",
}

REQUIRED_JOB_PERMISSIONS: dict[str, dict[str, tuple[str, ...]]] = {
    "ci.yml": {"security-matrix": ("permissions:", "security-events: write", "contents: read")},
    "security-maintenance.yml": {"security-maintenance": ("permissions:", "contents: read")},
    "security-super-extended.yml": {"security-super-extended": ("permissions:", "contents: read")},
    "release.yml": {"verify-signatures": ("permissions:", "contents: read")},
}

_JOB_RE = re.compile(r"^  ([A-Za-z0-9_-]+):\s*$")
_PERMISSION_VALUE_RE = re.compile(r"^\s{2}([A-Za-z0-9_-]+):\s*([A-Za-z-]+)\s*$")


def _job_blocks(text: str) -> dict[str, str]:
    lines = text.splitlines()
    in_jobs = False
    current_job: str | None = None
    blocks: dict[str, list[str]] = {}

    for line in lines:
        if not in_jobs:
            if line.strip() == "jobs:":
                in_jobs = True
            continue
        match = _JOB_RE.match(line)
        if match:
            current_job = match.group(1)
            blocks[current_job] = []
            continue
        if line and not line.startswith(" "):
            break
        if current_job is not None:
            blocks[current_job].append(line)

    return {name: "\n".join(block) for name, block in blocks.items()}


def _workflow_permissions_values(text: str) -> list[tuple[str, str]]:
    lines = text.splitlines()
    values: list[tuple[str, str]] = []
    for idx, line in enumerate(lines):
        if line.strip() == "permissions:" and not line.startswith(" "):
            for inner in lines[idx + 1 :]:
                if not inner.strip():
                    continue
                if not inner.startswith("  "):
                    break
                if inner.startswith("    "):
                    continue
                match = _PERMISSION_VALUE_RE.match(inner)
                if match:
                    values.append((match.group(1), match.group(2)))
            break
        if line.startswith("permissions:") and line.strip() != "permissions:":
            _key, value = line.split(":", 1)
            values.append(("permissions", value.strip()))
            break
    return values


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    checked = 0
    security_workflows = 0
    wf_dir = ROOT / ".github" / "workflows"

    for wf in sorted(wf_dir.glob("*.yml")):
        text = wf.read_text(encoding="utf-8")
        blocks = _job_blocks(text)
        checked += 1
        rel = str(wf.relative_to(ROOT)).replace("\\", "/")
        if "write-all" in text:
            findings.append(f"forbidden_permission_write_all:{rel}")
        for key, value in _workflow_permissions_values(text):
            if value in {"write", "write-all"}:
                findings.append(f"forbidden_workflow_default_write_permission:{rel}:{key}:{value}")
        if wf.name in REQUIRED_EXPLICIT_PERMISSIONS:
            security_workflows += 1
            if "permissions:" not in text:
                findings.append(f"missing_permissions_block:{rel}")
        for job_name, required_snippets in REQUIRED_JOB_PERMISSIONS.get(wf.name, {}).items():
            block = blocks.get(job_name)
            if block is None:
                findings.append(f"missing_required_job:{rel}:{job_name}")
                continue
            for snippet in required_snippets:
                if snippet not in block:
                    findings.append(f"missing_required_job_permission:{rel}:{job_name}:{snippet}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"checked_workflows": checked, "security_workflows": security_workflows},
        "metadata": {"gate": "security_workflow_permissions_policy_gate"},
    }
    out = evidence_root() / "security" / "security_workflow_permissions_policy_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_WORKFLOW_PERMISSIONS_POLICY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
