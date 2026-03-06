#!/usr/bin/env python3
from __future__ import annotations

import importlib
import os
import re
import subprocess
import sys
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report
artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")

RATIONALE_FILE = "governance/security/workflow_change_rationale.md"
DEPENDENCY_POLICY = ROOT / "governance" / "security" / "security_workflow_dependency_policy.json"
STEP_BASELINE_FILE = ROOT / "governance" / "security" / "security_workflow_job_step_baseline.json"
CONDITION_BASELINE_FILE = ROOT / "governance" / "security" / "security_workflow_critical_step_conditions.json"
STRUCTURE_APPROVAL_FILE = ROOT / "governance" / "security" / "workflow_structure_change_approval.json"


def _changed_files() -> list[str]:
    env_value = str(os.environ.get("GLYPHSER_CHANGED_FILES", "")).strip()
    if env_value:
        return [item.strip() for item in env_value.split(",") if item.strip()]
    try:
        proc = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except Exception:
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


STEP_NAME_RE = re.compile(r"^\s*-\s+name:\s*(.+?)\s*$", re.MULTILINE)
UPLOAD_PATH_RE = re.compile(r"^\s+\$\{\{\s*env\.[A-Za-z0-9_]+\s*\}\}/[^\s#]+$", re.MULTILINE)


def _step_order_findings() -> list[str]:
    findings: list[str] = []
    if not DEPENDENCY_POLICY.exists():
        findings.append("missing_workflow_dependency_policy:governance/security/security_workflow_dependency_policy.json")
        return findings

    payload = _read_json(DEPENDENCY_POLICY)
    checks = payload.get("step_order_checks", []) if isinstance(payload, dict) else []
    if not isinstance(checks, list):
        return ["invalid_workflow_dependency_policy:step_order_checks_not_list"]

    for raw in checks:
        if not isinstance(raw, dict):
            findings.append("invalid_step_order_check:not_object")
            continue
        workflow = str(raw.get("workflow", "")).strip()
        ordered_steps = [str(item).strip() for item in raw.get("ordered_steps", []) if isinstance(item, str) and str(item).strip()]
        if not workflow or not ordered_steps:
            findings.append("invalid_step_order_check:missing_workflow_or_ordered_steps")
            continue
        wf_path = ROOT / workflow
        if not wf_path.exists():
            findings.append(f"missing_workflow_for_dependency_check:{workflow}")
            continue
        text = wf_path.read_text(encoding="utf-8", errors="ignore")
        step_names = [match.group(1).strip() for match in STEP_NAME_RE.finditer(text)]
        index_map: dict[str, int] = {}
        for idx, name in enumerate(step_names):
            index_map.setdefault(name, idx)
        for step in ordered_steps:
            if step not in index_map:
                findings.append(f"workflow_dependency_step_missing:{workflow}:{step}")
        for earlier, later in zip(ordered_steps, ordered_steps[1:]):
            if earlier in index_map and later in index_map and index_map[earlier] > index_map[later]:
                findings.append(f"workflow_dependency_order_violation:{workflow}:{earlier}>{later}")
    return findings


def _required_env_findings() -> list[str]:
    findings: list[str] = []
    if not DEPENDENCY_POLICY.exists():
        findings.append("missing_workflow_dependency_policy:governance/security/security_workflow_dependency_policy.json")
        return findings
    payload = _read_json(DEPENDENCY_POLICY)
    checks = payload.get("required_env_checks", []) if isinstance(payload, dict) else []
    if not isinstance(checks, list):
        return ["invalid_workflow_dependency_policy:required_env_checks_not_list"]

    for raw in checks:
        if not isinstance(raw, dict):
            findings.append("invalid_required_env_check:not_object")
            continue
        workflow = str(raw.get("workflow", "")).strip()
        required_env_vars = [
            str(item).strip() for item in raw.get("required_env_vars", []) if isinstance(item, str) and str(item).strip()
        ]
        if not workflow or not required_env_vars:
            findings.append("invalid_required_env_check:missing_workflow_or_required_env_vars")
            continue
        wf_path = ROOT / workflow
        if not wf_path.exists():
            findings.append(f"missing_workflow_for_required_env_check:{workflow}")
            continue
        text = wf_path.read_text(encoding="utf-8", errors="ignore")
        for env_var in required_env_vars:
            if re.search(rf"(^|\\s){re.escape(env_var)}\\s*:", text, flags=re.MULTILINE) is None:
                findings.append(f"missing_required_env_var:{workflow}:{env_var}")
    return findings


def _artifact_upload_path_findings() -> list[str]:
    findings: list[str] = []
    if not DEPENDENCY_POLICY.exists():
        findings.append("missing_workflow_dependency_policy:governance/security/security_workflow_dependency_policy.json")
        return findings
    payload = _read_json(DEPENDENCY_POLICY)
    checks = payload.get("artifact_upload_path_baselines", []) if isinstance(payload, dict) else []
    if not isinstance(checks, list):
        return ["invalid_workflow_dependency_policy:artifact_upload_path_baselines_not_list"]

    for raw in checks:
        if not isinstance(raw, dict):
            findings.append("invalid_artifact_upload_baseline_check:not_object")
            continue
        workflow = str(raw.get("workflow", "")).strip()
        baseline_path = str(raw.get("baseline", "")).strip()
        if not workflow or not baseline_path:
            findings.append("invalid_artifact_upload_baseline_check:missing_workflow_or_baseline")
            continue
        wf_path = ROOT / workflow
        baseline = ROOT / baseline_path
        if not wf_path.exists():
            findings.append(f"missing_workflow_for_artifact_upload_check:{workflow}")
            continue
        if not baseline.exists():
            findings.append(f"missing_artifact_upload_baseline:{baseline_path}")
            continue

        baseline_payload = _read_json(baseline)
        expected_paths = {
            str(item).strip()
            for item in baseline_payload.get("upload_paths", [])
            if isinstance(item, str) and str(item).strip()
        }
        workflow_text = wf_path.read_text(encoding="utf-8", errors="ignore")
        observed_paths = {m.group(0).strip() for m in UPLOAD_PATH_RE.finditer(workflow_text)}
        if expected_paths != observed_paths:
            findings.append(f"artifact_upload_paths_drift:{workflow}")
    return findings


def _parse_bracket_list(value: str) -> list[str]:
    inner = value.strip()
    if inner.startswith("[") and inner.endswith("]"):
        inner = inner[1:-1]
    parts = [item.strip().strip('"').strip("'") for item in inner.split(",")]
    return [item for item in parts if item]


def _matrix_shrinkage_findings() -> list[str]:
    findings: list[str] = []
    if not DEPENDENCY_POLICY.exists():
        findings.append("missing_workflow_dependency_policy:governance/security/security_workflow_dependency_policy.json")
        return findings
    payload = _read_json(DEPENDENCY_POLICY)
    checks = payload.get("matrix_minimums", []) if isinstance(payload, dict) else []
    if not isinstance(checks, list):
        return ["invalid_workflow_dependency_policy:matrix_minimums_not_list"]

    for raw in checks:
        if not isinstance(raw, dict):
            findings.append("invalid_matrix_minimum_check:not_object")
            continue
        workflow = str(raw.get("workflow", "")).strip()
        key = str(raw.get("key", "")).strip()
        minimum_entries = int(raw.get("minimum_entries", 0))
        required_values = [str(item).strip() for item in raw.get("required_values", []) if isinstance(item, str) and str(item).strip()]
        if not workflow or not key or minimum_entries <= 0:
            findings.append("invalid_matrix_minimum_check:missing_workflow_key_or_minimum")
            continue
        wf_path = ROOT / workflow
        if not wf_path.exists():
            findings.append(f"missing_workflow_for_matrix_check:{workflow}")
            continue
        text = wf_path.read_text(encoding="utf-8", errors="ignore")
        match = re.search(rf"^\s*{re.escape(key)}:\s*(\[[^\]]*\])\s*$", text, flags=re.MULTILINE)
        if match is None:
            findings.append(f"missing_matrix_key:{workflow}:{key}")
            continue
        values = _parse_bracket_list(match.group(1))
        if len(values) < minimum_entries:
            findings.append(f"matrix_shrinkage_detected:{workflow}:{key}:{len(values)}<{minimum_entries}")
        for required in required_values:
            if required not in values:
                findings.append(f"matrix_required_value_missing:{workflow}:{key}:{required}")
    return findings


def _parse_ts(text: str) -> datetime | None:
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
    except Exception:
        return None


WORKFLOW_JOB_RE = re.compile(r"^  ([A-Za-z0-9_-]+):\s*$")
WORKFLOW_STEPS_RE = re.compile(r"^\s{4}steps:\s*$")
WORKFLOW_STEP_NAME_RE = re.compile(r"^\s{6}-\s+name:\s*(.+?)\s*$")
WORKFLOW_STEP_IF_RE = re.compile(r"^\s{8}if:\s*(.+?)\s*$")
WORKFLOW_STEP_RUN_RE = re.compile(r"^\s{8}run:\s*(.*)$")
WORKFLOW_STEP_WORKDIR_RE = re.compile(r"^\s{8}working-directory:\s*(.+?)\s*$")
WORKFLOW_STEP_USES_RE = re.compile(r"^\s{6}-\s+uses:\s*(.+?)\s*$")
PINNED_CHECKOUT_RE = re.compile(r"^actions/checkout@[0-9a-f]{40}$")


def _extract_job_step_names(workflow_text: str) -> dict[str, list[str]]:
    in_jobs = False
    current_job = ""
    in_steps = False
    steps_by_job: dict[str, list[str]] = {}
    for line in workflow_text.splitlines():
        if not in_jobs:
            if line.strip() == "jobs:":
                in_jobs = True
            continue
        if line and not line.startswith(" "):
            break

        job_match = WORKFLOW_JOB_RE.match(line)
        if job_match:
            current_job = job_match.group(1).strip()
            in_steps = False
            continue
        if not current_job:
            continue
        if WORKFLOW_STEPS_RE.match(line):
            in_steps = True
            steps_by_job.setdefault(current_job, [])
            continue
        if in_steps:
            if line.startswith("    ") and not line.startswith("      "):
                in_steps = False
                continue
            step_match = WORKFLOW_STEP_NAME_RE.match(line)
            if step_match:
                steps_by_job.setdefault(current_job, []).append(step_match.group(1).strip())
    return steps_by_job


def _extract_job_step_if_conditions(workflow_text: str) -> dict[str, dict[str, str]]:
    in_jobs = False
    current_job = ""
    in_steps = False
    current_step = ""
    conditions: dict[str, dict[str, str]] = {}
    for line in workflow_text.splitlines():
        if not in_jobs:
            if line.strip() == "jobs:":
                in_jobs = True
            continue
        if line and not line.startswith(" "):
            break

        job_match = WORKFLOW_JOB_RE.match(line)
        if job_match:
            current_job = job_match.group(1).strip()
            in_steps = False
            current_step = ""
            continue
        if not current_job:
            continue
        if WORKFLOW_STEPS_RE.match(line):
            in_steps = True
            conditions.setdefault(current_job, {})
            continue
        if in_steps:
            if line.startswith("    ") and not line.startswith("      "):
                in_steps = False
                current_step = ""
                continue
            step_match = WORKFLOW_STEP_NAME_RE.match(line)
            if step_match:
                current_step = step_match.group(1).strip()
                conditions.setdefault(current_job, {})[current_step] = ""
                continue
            if_match = WORKFLOW_STEP_IF_RE.match(line)
            if if_match and current_step:
                conditions.setdefault(current_job, {})[current_step] = if_match.group(1).strip()
    return conditions


def _extract_job_step_runs(workflow_text: str) -> dict[str, dict[str, str]]:
    in_jobs = False
    current_job = ""
    in_steps = False
    current_step = ""
    runs: dict[str, dict[str, str]] = {}
    lines = workflow_text.splitlines()
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        if not in_jobs:
            if line.strip() == "jobs:":
                in_jobs = True
            idx += 1
            continue
        if line and not line.startswith(" "):
            break
        job_match = WORKFLOW_JOB_RE.match(line)
        if job_match:
            current_job = job_match.group(1).strip()
            in_steps = False
            current_step = ""
            idx += 1
            continue
        if not current_job:
            idx += 1
            continue
        if WORKFLOW_STEPS_RE.match(line):
            in_steps = True
            runs.setdefault(current_job, {})
            idx += 1
            continue
        if in_steps:
            if line.startswith("    ") and not line.startswith("      "):
                in_steps = False
                current_step = ""
                idx += 1
                continue
            step_match = WORKFLOW_STEP_NAME_RE.match(line)
            if step_match:
                current_step = step_match.group(1).strip()
                runs.setdefault(current_job, {}).setdefault(current_step, "")
                idx += 1
                continue
            run_match = WORKFLOW_STEP_RUN_RE.match(line)
            if run_match and current_step:
                rhs = run_match.group(1).strip()
                if rhs in {"|", ">", "|-", ">-", ""}:
                    block: list[str] = []
                    idx += 1
                    while idx < len(lines):
                        nxt = lines[idx]
                        if nxt.startswith("          "):
                            block.append(nxt[10:])
                            idx += 1
                            continue
                        break
                    runs.setdefault(current_job, {})[current_step] = "\n".join(block).strip()
                    continue
                runs.setdefault(current_job, {})[current_step] = rhs
                idx += 1
                continue
        idx += 1
    return runs


def _security_workflow_paths(changed: list[str]) -> list[str]:
    out: list[str] = []
    for path in changed:
        if not path.startswith(".github/workflows/"):
            continue
        name = Path(path).name.lower()
        if "security" in name or name == "release.yml" or name == "ci.yml":
            out.append(path)
    return sorted(set(out))


def _validate_structure_approval(changed: list[str], required_workflows: set[str]) -> list[str]:
    findings: list[str] = []
    approval_rel = str(STRUCTURE_APPROVAL_FILE.relative_to(ROOT)).replace("\\", "/")
    sig_rel = f"{approval_rel}.sig"
    if approval_rel not in changed:
        findings.append("missing_updated_workflow_structure_change_approval_file")
    if sig_rel not in changed:
        findings.append("missing_updated_workflow_structure_change_approval_signature")
    if not STRUCTURE_APPROVAL_FILE.exists():
        findings.append("missing_workflow_structure_change_approval_file")
        return findings

    record = _read_json(STRUCTURE_APPROVAL_FILE)
    if not isinstance(record, dict):
        findings.append("invalid_workflow_structure_change_approval_file")
        return findings
    for field in ("ticket", "rationale", "approved_by", "approved_at_utc", "expires_at_utc"):
        if not str(record.get(field, "")).strip():
            findings.append(f"missing_workflow_structure_change_approval_field:{field}")
    approved_at = _parse_ts(str(record.get("approved_at_utc", "")))
    expires_at = _parse_ts(str(record.get("expires_at_utc", "")))
    now = datetime.now(UTC)
    if approved_at is None:
        findings.append("invalid_workflow_structure_change_approved_at")
    if expires_at is None:
        findings.append("invalid_workflow_structure_change_expires_at")
    if approved_at and expires_at and approved_at > expires_at:
        findings.append("workflow_structure_change_approval_time_range_invalid")
    if expires_at and expires_at < now:
        findings.append("workflow_structure_change_approval_expired")
    covered_workflows = record.get("workflow_paths", [])
    if not isinstance(covered_workflows, list):
        findings.append("invalid_workflow_structure_change_approval_workflow_paths")
    else:
        covered = {str(item).strip() for item in covered_workflows if str(item).strip()}
        for workflow in required_workflows:
            if workflow not in covered:
                findings.append(f"workflow_structure_change_approval_missing_workflow:{workflow}")

    sig_path = STRUCTURE_APPROVAL_FILE.with_suffix(".json.sig")
    if not sig_path.exists():
        findings.append("missing_workflow_structure_change_approval_signature")
    else:
        signature = sig_path.read_text(encoding="utf-8").strip()
        key = artifact_signing.current_key(strict=False)
        if not artifact_signing.verify_file(STRUCTURE_APPROVAL_FILE, signature, key=key):
            findings.append("invalid_workflow_structure_change_approval_signature")
    return findings


def _step_insertion_removal_findings(changed: list[str]) -> tuple[list[str], bool]:
    findings: list[str] = []
    if not STEP_BASELINE_FILE.exists():
        findings.append("missing_security_workflow_job_step_baseline")
        return findings, False
    payload = _read_json(STEP_BASELINE_FILE)
    workflows = payload.get("workflows", {}) if isinstance(payload, dict) else {}
    if not isinstance(workflows, dict):
        return ["invalid_security_workflow_job_step_baseline"], False

    security_workflows = _security_workflow_paths(changed)
    step_drift_detected = False
    drift_events: list[str] = []
    drift_workflows: set[str] = set()
    for workflow in security_workflows:
        expected_entry = workflows.get(workflow)
        if not isinstance(expected_entry, dict):
            continue
        expected_jobs = expected_entry.get("jobs", {})
        if not isinstance(expected_jobs, dict):
            findings.append(f"invalid_step_baseline_jobs:{workflow}")
            continue
        wf_path = ROOT / workflow
        if not wf_path.exists():
            findings.append(f"missing_security_workflow_for_step_baseline:{workflow}")
            continue
        observed_jobs = _extract_job_step_names(wf_path.read_text(encoding="utf-8", errors="ignore"))
        for job_name, expected_steps_raw in expected_jobs.items():
            if not isinstance(job_name, str) or not isinstance(expected_steps_raw, list):
                findings.append(f"invalid_step_baseline_job_entry:{workflow}")
                continue
            expected_steps = [str(item).strip() for item in expected_steps_raw if str(item).strip()]
            observed_steps = observed_jobs.get(job_name, [])
            inserted = [name for name in observed_steps if name not in expected_steps]
            removed = [name for name in expected_steps if name not in observed_steps]
            if inserted or removed:
                step_drift_detected = True
                drift_workflows.add(workflow)
                details: list[str] = []
                if inserted:
                    details.append("inserted=" + ",".join(inserted))
                if removed:
                    details.append("removed=" + ",".join(removed))
                drift_events.append(f"security_step_structure_drift:{workflow}:{job_name}:{'|'.join(details)}")
    if not step_drift_detected:
        return findings, False
    approval_findings = _validate_structure_approval(changed, drift_workflows)
    if approval_findings:
        findings.extend(approval_findings)
        findings.extend(drift_events)
    return findings, True


def _critical_step_condition_findings(changed: list[str]) -> tuple[list[str], bool]:
    findings: list[str] = []
    if not CONDITION_BASELINE_FILE.exists():
        findings.append("missing_security_workflow_critical_step_conditions_baseline")
        return findings, False
    payload = _read_json(CONDITION_BASELINE_FILE)
    checks = payload.get("critical_step_conditions", []) if isinstance(payload, dict) else []
    if not isinstance(checks, list):
        return ["invalid_security_workflow_critical_step_conditions_baseline"], False

    security_workflows = set(_security_workflow_paths(changed))
    condition_drift_detected = False
    drift_events: list[str] = []
    drift_workflows: set[str] = set()
    cache: dict[str, dict[str, dict[str, str]]] = {}
    for raw in checks:
        if not isinstance(raw, dict):
            findings.append("invalid_critical_step_condition_check:not_object")
            continue
        workflow = str(raw.get("workflow", "")).strip()
        job = str(raw.get("job", "")).strip()
        step = str(raw.get("step", "")).strip()
        expected_if = str(raw.get("if", "")).strip()
        if not workflow or not job or not step:
            findings.append("invalid_critical_step_condition_check:missing_workflow_job_or_step")
            continue
        if workflow not in security_workflows:
            continue
        wf_path = ROOT / workflow
        if not wf_path.exists():
            findings.append(f"missing_security_workflow_for_condition_baseline:{workflow}")
            continue
        if workflow not in cache:
            cache[workflow] = _extract_job_step_if_conditions(wf_path.read_text(encoding="utf-8", errors="ignore"))
        observed_if = cache[workflow].get(job, {}).get(step, "")
        if observed_if.strip() != expected_if:
            condition_drift_detected = True
            drift_workflows.add(workflow)
            drift_events.append(
                f"critical_step_condition_drift:{workflow}:{job}:{step}:expected={expected_if or '<none>'}:observed={observed_if or '<none>'}"
            )
    if not condition_drift_detected:
        return findings, False
    approval_findings = _validate_structure_approval(changed, drift_workflows)
    if approval_findings:
        findings.extend(approval_findings)
        findings.extend(drift_events)
    return findings, True


PIPE_RE = re.compile(r"(?<!\|)\|(?!\|)")


def _shell_option_weakening_findings(changed: list[str]) -> tuple[list[str], bool]:
    findings: list[str] = []
    weakening_detected = False
    for workflow in _security_workflow_paths(changed):
        wf_path = ROOT / workflow
        if not wf_path.exists():
            continue
        runs = _extract_job_step_runs(wf_path.read_text(encoding="utf-8", errors="ignore"))
        for job, steps in runs.items():
            for step, script in steps.items():
                text = script.strip()
                if not text:
                    continue
                low = text.lower()
                if "set +e" in low:
                    weakening_detected = True
                    findings.append(f"security_shell_option_weakening_set_plus_e:{workflow}:{job}:{step}")
                if PIPE_RE.search(text) and "pipefail" not in low:
                    weakening_detected = True
                    findings.append(f"security_shell_option_weakening_unchecked_pipe:{workflow}:{job}:{step}")
                if re.search(r"\|\|\s*(?:true|:)\b", low):
                    weakening_detected = True
                    findings.append(f"security_shell_option_weakening_ignored_return:{workflow}:{job}:{step}")
    return findings, weakening_detected


def _cwd_and_trusted_context_findings(changed: list[str]) -> tuple[list[str], bool]:
    findings: list[str] = []
    detected = False
    if not DEPENDENCY_POLICY.exists():
        return findings, False
    payload = _read_json(DEPENDENCY_POLICY)
    checks = payload.get("trusted_context_checks", []) if isinstance(payload, dict) else []
    if not isinstance(checks, list):
        return ["invalid_workflow_dependency_policy:trusted_context_checks_not_list"], False
    configured = {str(item).strip() for item in checks if isinstance(item, str) and str(item).strip()}
    for workflow in _security_workflow_paths(changed):
        if workflow not in configured:
            continue
        wf_path = ROOT / workflow
        if not wf_path.exists():
            continue
        text = wf_path.read_text(encoding="utf-8", errors="ignore")
        lines = text.splitlines()
        in_jobs = False
        current_job = ""
        in_steps = False
        current_step = ""
        current_has_run = False
        current_has_workdir = False
        checkout_pinned = False
        job_default_workdir: dict[str, bool] = {}

        def finalize_step() -> None:
            nonlocal detected, findings, current_step, current_has_run, current_has_workdir, current_job
            if current_step and current_has_run:
                if not current_has_workdir and not job_default_workdir.get(current_job, False):
                    detected = True
                    findings.append(f"security_step_missing_explicit_cwd:{workflow}:{current_job}:{current_step}")
            current_step = ""
            current_has_run = False
            current_has_workdir = False

        idx = 0
        while idx < len(lines):
            line = lines[idx]
            if not in_jobs:
                if line.strip() == "jobs:":
                    in_jobs = True
                idx += 1
                continue
            if line and not line.startswith(" "):
                finalize_step()
                break

            job_match = WORKFLOW_JOB_RE.match(line)
            if job_match:
                finalize_step()
                current_job = job_match.group(1).strip()
                in_steps = False
                job_default_workdir.setdefault(current_job, False)
                idx += 1
                continue

            if current_job:
                if re.match(r"^\s{4}defaults:\s*$", line):
                    window = "\n".join(lines[idx : idx + 8])
                    if re.search(r"^\s{6}run:\s*$", window, flags=re.MULTILINE) and re.search(
                        r"^\s{8}working-directory:\s*.+$", window, flags=re.MULTILINE
                    ):
                        job_default_workdir[current_job] = True
                if WORKFLOW_STEPS_RE.match(line):
                    in_steps = True
                    idx += 1
                    continue
                if in_steps:
                    if line.startswith("    ") and not line.startswith("      "):
                        finalize_step()
                        in_steps = False
                        idx += 1
                        continue
                    uses_match = WORKFLOW_STEP_USES_RE.match(line)
                    if uses_match and PINNED_CHECKOUT_RE.match(uses_match.group(1).strip()):
                        checkout_pinned = True
                    step_name_match = WORKFLOW_STEP_NAME_RE.match(line)
                    if step_name_match:
                        finalize_step()
                        current_step = step_name_match.group(1).strip()
                        idx += 1
                        continue
                    if WORKFLOW_STEP_RUN_RE.match(line):
                        current_has_run = True
                    if WORKFLOW_STEP_WORKDIR_RE.match(line):
                        current_has_workdir = True
            idx += 1
        finalize_step()
        if not checkout_pinned:
            detected = True
            findings.append(f"security_workflow_missing_trusted_repo_context:{workflow}")
    return findings, detected


def main(argv: list[str] | None = None) -> int:
    _ = argv
    changed = _changed_files()
    findings: list[str] = []
    findings.extend(_step_order_findings())
    findings.extend(_required_env_findings())
    findings.extend(_artifact_upload_path_findings())
    findings.extend(_matrix_shrinkage_findings())
    structure_findings, structure_drift_detected = _step_insertion_removal_findings(changed)
    findings.extend(structure_findings)
    condition_findings, condition_drift_detected = _critical_step_condition_findings(changed)
    findings.extend(condition_findings)
    shell_findings, shell_weakening_detected = _shell_option_weakening_findings(changed)
    findings.extend(shell_findings)
    cwd_findings, cwd_context_detected = _cwd_and_trusted_context_findings(changed)
    findings.extend(cwd_findings)

    workflow_changes = sorted(p for p in changed if p.startswith(".github/workflows/") and "security" in p)
    policy_changes = sorted(p for p in changed if p.startswith("governance/security/") and p.endswith(".json"))
    rationale_changed = RATIONALE_FILE in changed
    rationale_env = str(os.environ.get("GLYPHSER_WORKFLOW_CHANGE_RATIONALE", "")).strip()

    if workflow_changes and not policy_changes and not rationale_changed and not rationale_env:
        findings.append("security_workflow_change_missing_policy_diff_or_rationale")
    for wf in workflow_changes:
        if not (policy_changes or rationale_changed or rationale_env):
            findings.append(f"unjustified_security_workflow_change:{wf}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "changed_files": len(changed),
            "security_workflow_changes": workflow_changes,
            "policy_changes": policy_changes,
            "rationale_changed": rationale_changed,
            "rationale_provided": bool(rationale_env),
            "workflow_step_structure_drift_detected": structure_drift_detected,
            "critical_step_condition_drift_detected": condition_drift_detected,
            "shell_option_weakening_detected": shell_weakening_detected,
            "cwd_trusted_context_violations_detected": cwd_context_detected,
        },
        "metadata": {"gate": "workflow_change_management_gate"},
    }
    out = evidence_root() / "security" / "workflow_change_management_gate.json"
    write_json_report(out, report)
    print(f"WORKFLOW_CHANGE_MANAGEMENT_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
