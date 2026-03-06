#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import json
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

WORKFLOWS_DIR = ROOT / ".github" / "workflows"
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _normalize_command(command: str) -> str:
    lines = [line.rstrip() for line in command.replace("\r\n", "\n").split("\n")]
    return "\n".join(lines).strip()


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _normalize_env(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    normalized: dict[str, str] = {}
    for key, item in value.items():
        name = str(key).strip()
        if not name:
            continue
        normalized[name] = str(item)
    return normalized


def _env_hash(merged_env: dict[str, str]) -> str:
    canonical = json.dumps(merged_env, sort_keys=True, separators=(",", ":"))
    return _hash_text(canonical)


def _collect_fingerprints() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for workflow_path in sorted(WORKFLOWS_DIR.glob("*.yml")):
        payload = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            continue
        workflow_env = _normalize_env(payload.get("env", {}))
        jobs = payload.get("jobs", {})
        if not isinstance(jobs, dict):
            continue
        for job_name, job_payload in sorted(jobs.items()):
            if not isinstance(job_payload, dict):
                continue
            job_env = dict(workflow_env)
            job_env.update(_normalize_env(job_payload.get("env", {})))
            steps = job_payload.get("steps", [])
            if not isinstance(steps, list):
                continue
            for idx, step in enumerate(steps):
                if not isinstance(step, dict):
                    continue
                run_cmd = step.get("run")
                if not isinstance(run_cmd, str) or not run_cmd.strip():
                    continue
                step_name = str(step.get("name", f"step-{idx}")).strip() or f"step-{idx}"
                step_env = dict(job_env)
                step_env.update(_normalize_env(step.get("env", {})))
                normalized = _normalize_command(run_cmd)
                run_correlation_id = step_env.get("GLYPHSER_RUN_CORRELATION_ID", "").strip() or step_env.get(
                    "GITHUB_RUN_ID", ""
                ).strip()
                rows.append(
                    {
                        "workflow": str(workflow_path.relative_to(ROOT)).replace("\\", "/"),
                        "job": str(job_name),
                        "step_index": idx,
                        "step_name": step_name,
                        "command_hash_sha256": _hash_text(normalized),
                        "env_profile_hash_sha256": _env_hash(step_env),
                        "start_marker": f"STEP_START:{job_name}:{idx}:{_hash_text(step_name)[:12]}",
                        "end_marker": f"STEP_END:{job_name}:{idx}:{_hash_text(step_name)[:12]}",
                        "run_correlation_id": run_correlation_id,
                    }
                )
    return rows


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    fingerprints = _collect_fingerprints()
    if not fingerprints:
        findings.append("no_security_workflow_run_steps_found")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"fingerprinted_steps": len(fingerprints)},
        "metadata": {"gate": "security_step_execution_fingerprint"},
        "fingerprints": fingerprints,
    }
    out = evidence_root() / "security" / "security_step_execution_fingerprint.json"
    write_json_report(out, report)
    print(f"SECURITY_STEP_EXECUTION_FINGERPRINT: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
