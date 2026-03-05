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

WORKFLOWS_DIR = ROOT / ".github" / "workflows"
UPLOAD_STEP_RE = re.compile(
    r"-\s+name:\s*(?P<step>.+?)\n(?P<body>(?:\s{6,}.+\n)+)",
    re.MULTILINE,
)


def _security_workflows() -> list[Path]:
    if not WORKFLOWS_DIR.exists():
        return []
    return sorted(path for path in WORKFLOWS_DIR.glob("*.yml") if "security" in path.name)


def _step_uses_upload(body: str) -> bool:
    return "uses: actions/upload-artifact" in body


def _step_name_field(body: str) -> str:
    for raw in body.splitlines():
        line = raw.strip()
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip()
    return ""


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    checked_steps = 0

    for workflow in _security_workflows():
        lane_id = workflow.stem.replace("_", "-")
        text = workflow.read_text(encoding="utf-8")
        for match in UPLOAD_STEP_RE.finditer(text):
            body = match.group("body")
            if not _step_uses_upload(body):
                continue
            checked_steps += 1
            artifact_name = _step_name_field(body)
            if not artifact_name:
                findings.append(f"missing_upload_artifact_name:{workflow.name}:{match.group('step').strip()}")
                continue
            if "${{ github.job }}" in artifact_name:
                continue
            if lane_id not in artifact_name and "security" not in artifact_name.lower():
                findings.append(f"artifact_name_missing_lane_identifier:{workflow.name}:{artifact_name}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "upload_steps_checked": checked_steps,
            "violations": len(findings),
        },
        "metadata": {"validator": "security_artifact_lane_name_validator"},
    }
    out = evidence_root() / "security" / "security_artifact_lane_name_validator.json"
    write_json_report(out, report)
    print(f"SECURITY_ARTIFACT_LANE_NAME_VALIDATOR: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
