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


def _looks_dynamic(name: str) -> bool:
    dynamic_tokens = (
        "${{ github.job }}",
        "${{ github.run_id }}",
        "${{ github.run_number }}",
        "${{ github.run_attempt }}",
        "${{ github.workflow }}",
        "${{ matrix.",
    )
    return any(token in name for token in dynamic_tokens)


def _has_lane_discriminator(name: str, lane_id: str) -> bool:
    return lane_id in name or "${{ github.job }}" in name or "${{ github.workflow }}" in name or "${{ matrix." in name


def _has_run_discriminator(name: str) -> bool:
    return (
        "${{ github.run_id }}" in name
        or "${{ github.run_number }}" in name
        or "${{ github.run_attempt }}" in name
    )


def _step_paths(body: str) -> list[str]:
    lines = body.splitlines()
    in_path = False
    out: list[str] = []
    for raw in lines:
        stripped = raw.strip()
        if stripped.startswith("path:"):
            value = stripped.split(":", 1)[1].strip()
            if value:
                out.append(value)
            in_path = True
            continue
        if in_path:
            if raw.startswith(" " * 10):
                token = stripped
                if token:
                    out.append(token)
                continue
            in_path = False
    return out


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    checked_steps = 0
    artifact_names: dict[str, set[str]] = {}
    allowed_suffixes = {".json", ".sarif", ".xml", ".md", ".txt", ".html", ".csv", ".sig", ".jsonl"}

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
            artifact_names.setdefault(artifact_name, set()).add(workflow.name)
            if not _has_lane_discriminator(artifact_name, lane_id) and "security" not in artifact_name.lower():
                findings.append(f"artifact_name_missing_lane_identifier:{workflow.name}:{artifact_name}")
            if not _has_run_discriminator(artifact_name):
                findings.append(f"artifact_name_missing_run_discriminator:{workflow.name}:{artifact_name}")
            for relpath in _step_paths(body):
                filename = Path(relpath.rstrip("/")).name
                if not filename or filename.startswith("${{"):
                    continue
                if filename.startswith("."):
                    findings.append(f"hidden_artifact_path:{workflow.name}:{artifact_name}:{relpath}")
                if relpath.endswith("/") or "." not in filename:
                    continue
                suffix = Path(filename).suffix.lower()
                if suffix not in allowed_suffixes:
                    findings.append(f"ambiguous_artifact_extension:{workflow.name}:{artifact_name}:{relpath}")
            step_paths = [path for path in _step_paths(body) if path and not path.endswith("/")]
            path_set = set(step_paths)
            for relpath in step_paths:
                if not relpath.endswith(".sig"):
                    continue
                target = relpath[:-4]
                target_name = Path(target).name
                if "." not in target_name:
                    findings.append(f"signature_basename_mismatch:{workflow.name}:{artifact_name}:{relpath}")
                    continue
                if target not in path_set:
                    findings.append(f"signature_without_matching_artifact:{workflow.name}:{artifact_name}:{relpath}")

    for artifact_name, owners in sorted(artifact_names.items()):
        if len(owners) <= 1 or _looks_dynamic(artifact_name):
            continue
        findings.append(f"duplicate_artifact_name_across_workflows:{artifact_name}:{','.join(sorted(owners))}")

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
