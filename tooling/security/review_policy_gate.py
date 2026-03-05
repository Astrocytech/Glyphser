#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import sys
from datetime import UTC, datetime
from fnmatch import fnmatch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
run_checked = importlib.import_module("tooling.security.subprocess_policy").run_checked
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _run(cmd: list[str]) -> str:
    proc = run_checked(cmd, cwd=ROOT)
    return proc.stdout.strip() if proc.returncode == 0 else ""


def _ticket_present(patterns: list[str]) -> bool:
    candidates = [
        os.environ.get("GLYPHSER_CHANGE_TICKET", ""),
        os.environ.get("GITHUB_HEAD_REF", ""),
        os.environ.get("GITHUB_REF_NAME", ""),
        _run(["git", "log", "-1", "--pretty=%B", "--", "."]),
    ]
    return any(pattern and pattern in candidate for pattern in patterns for candidate in candidates if candidate)


def _normalize_owner_path(text: str) -> str:
    cleaned = text.strip()
    if not cleaned:
        return ""
    if cleaned.startswith("/"):
        cleaned = cleaned[1:]
    cleaned = cleaned.replace("**", "")
    if cleaned.endswith("*"):
        cleaned = cleaned[:-1]
    return cleaned


def _covers_required_path(required: str, declared_paths: list[str]) -> bool:
    req = _normalize_owner_path(required)
    if not req:
        return False
    for declared in declared_paths:
        dec = _normalize_owner_path(declared)
        if not dec:
            continue
        if req.startswith(dec) or dec.startswith(req):
            return True
    return False


def _matches_path_pattern(path: str, pattern: str) -> bool:
    clean_pattern = pattern.strip().lstrip("/")
    if not clean_pattern:
        return False
    return fnmatch(path, clean_pattern)


def _parse_utc(value: str) -> datetime | None:
    raw = value.strip()
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = f"{raw[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None
    return parsed.astimezone(UTC) if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = json.loads((ROOT / "governance" / "security" / "review_policy.json").read_text(encoding="utf-8"))
    findings: list[str] = []
    advisories: list[str] = []
    enforce_ticket = bool(policy.get("enforce_change_ticket", False))
    enforce_changelog = bool(policy.get("enforce_changelog_entry", False))

    codeowners = ROOT / ".github" / "CODEOWNERS"
    if not codeowners.exists():
        findings.append("missing_codeowners")
    else:
        declared_paths: list[str] = []
        for raw in codeowners.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            declared_paths.append(line.split()[0])
        for path in policy.get("required_codeowners_paths", []):
            if isinstance(path, str) and not _covers_required_path(path, declared_paths):
                findings.append(f"missing_codeowner_rule:{path}")

    bp = json.loads((ROOT / ".github" / "branch-protection.required.json").read_text(encoding="utf-8"))
    min_approvals = int(policy.get("minimum_required_approvals", 2))
    if int(bp.get("minimum_required_approvals", 0)) < min_approvals:
        findings.append("branch_protection_approvals_too_low")

    changed = _run(["git", "diff", "--name-only", "HEAD~1", "HEAD", "--", "."]).splitlines()
    baseline_paths = [p for p in policy.get("security_baseline_paths", []) if isinstance(p, str)]
    if any(p in changed for p in baseline_paths):
        patterns = [p for p in policy.get("required_change_ticket_patterns", []) if isinstance(p, str)]
        if not _ticket_present(patterns):
            marker = "baseline_change_missing_ticket_or_adr"
            (findings if enforce_ticket else advisories).append(marker)

    security_paths = [
        p
        for p in changed
        if p.startswith("tooling/security/")
        or p.startswith("governance/security/")
        or p.startswith("runtime/glyphser/security/")
        or p.startswith(".github/workflows/")
    ]
    split_role_cfg = policy.get("split_role_enforcement", {})
    if not isinstance(split_role_cfg, dict):
        split_role_cfg = {}
    critical_patterns_raw = split_role_cfg.get(
        "security_critical_paths",
        ["tooling/security/**", "governance/security/**", ".github/workflows/**", "runtime/glyphser/security/**"],
    )
    critical_patterns = [
        str(x).strip() for x in critical_patterns_raw if isinstance(x, str) and str(x).strip()
    ]
    split_role_paths = [
        p for p in changed if any(_matches_path_pattern(p, pattern) for pattern in critical_patterns)
    ]
    split_role_required = bool(split_role_cfg.get("enabled", True)) and bool(split_role_paths)
    author = (
        os.environ.get("GLYPHSER_PR_AUTHOR", "").strip()
        or os.environ.get("GITHUB_ACTOR", "").strip()
    )
    approvers = [
        x.strip()
        for x in os.environ.get("GLYPHSER_PR_APPROVERS", "").split(",")
        if x.strip()
    ]
    normalized_author = author.lower()
    normalized_approvers = {x.lower() for x in approvers}
    fail_if_metadata_missing = bool(split_role_cfg.get("fail_if_metadata_missing", False))
    if split_role_required:
        if not author or not approvers:
            marker = "split_role_metadata_unavailable"
            (findings if fail_if_metadata_missing else advisories).append(marker)
        elif normalized_approvers == {normalized_author}:
            findings.append("split_role_author_is_sole_approver")
            findings.append("reviewer_independence_author_is_sole_reviewer")

    freshness_cfg = policy.get("approval_freshness_enforcement", {})
    if not isinstance(freshness_cfg, dict):
        freshness_cfg = {}
    freshness_required = bool(freshness_cfg.get("enabled", True)) and bool(split_role_paths)
    freshness_fail_on_missing = bool(freshness_cfg.get("fail_if_metadata_missing", False))
    approval_time = _parse_utc(os.environ.get("GLYPHSER_APPROVAL_GRANTED_AT_UTC", ""))
    security_change_time = _parse_utc(os.environ.get("GLYPHSER_LAST_SECURITY_CHANGE_AT_UTC", ""))
    if freshness_required:
        if approval_time is None or security_change_time is None:
            marker = "approval_freshness_metadata_unavailable"
            (findings if freshness_fail_on_missing else advisories).append(marker)
        elif security_change_time > approval_time:
            findings.append("approval_stale_post_approval_changes_detected")

    competency_cfg = policy.get("reviewer_competency_mapping", {})
    if not isinstance(competency_cfg, dict):
        competency_cfg = {}
    domains_raw = competency_cfg.get(
        "domains",
        {
            "policy_changes": {
                "path_patterns": ["governance/security/**"],
                "required_group": "security-governance",
            },
            "workflow_changes": {
                "path_patterns": [".github/workflows/**"],
                "required_group": "release-engineering",
            },
            "runtime_security_changes": {
                "path_patterns": ["runtime/glyphser/security/**"],
                "required_group": "security-operations",
            },
            "security_tooling_changes": {
                "path_patterns": ["tooling/security/**"],
                "required_group": "security-architecture",
            },
        },
    )
    domains = domains_raw if isinstance(domains_raw, dict) else {}
    approver_groups = {
        x.strip().lower()
        for x in os.environ.get("GLYPHSER_PR_APPROVER_GROUPS", "").split(",")
        if x.strip()
    }
    competency_fail_on_missing = bool(competency_cfg.get("fail_if_metadata_missing", False))
    missing_competency_domains: list[str] = []
    matched_competency_domains: list[str] = []
    for domain_name, domain_payload in domains.items():
        if not isinstance(domain_payload, dict):
            continue
        patterns_raw = domain_payload.get("path_patterns", [])
        if not isinstance(patterns_raw, list):
            continue
        patterns = [str(x).strip() for x in patterns_raw if isinstance(x, str) and str(x).strip()]
        if not patterns:
            continue
        if not any(any(_matches_path_pattern(path, pattern) for pattern in patterns) for path in changed):
            continue
        matched_competency_domains.append(str(domain_name))
    if matched_competency_domains and not approver_groups:
        marker = "reviewer_competency_metadata_unavailable"
        (findings if competency_fail_on_missing else advisories).append(marker)
    elif matched_competency_domains:
        for domain_name, domain_payload in domains.items():
            if str(domain_name) not in matched_competency_domains or not isinstance(domain_payload, dict):
                continue
            required_group = str(domain_payload.get("required_group", "")).strip().lower()
            if required_group and required_group not in approver_groups:
                missing_competency_domains.append(str(domain_name))
                findings.append(f"missing_required_reviewer_group:{domain_name}:{required_group}")

    if security_paths:
        patterns = [p for p in policy.get("required_change_ticket_patterns", []) if isinstance(p, str)]
        if not _ticket_present(patterns):
            marker = "security_change_missing_ticket_or_adr"
            (findings if enforce_ticket else advisories).append(marker)
    changelog = str(policy.get("required_changelog_file", "")).strip()
    if security_paths and changelog and changelog not in changed:
        marker = "missing_security_changelog_entry"
        (findings if enforce_changelog else advisories).append(marker)

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "advisories": advisories,
        "summary": {"changed_files": len(changed), "security_changed_files": len(security_paths)},
        "metadata": {
            "gate": "review_policy_gate",
            "min_approvals": min_approvals,
            "enforce_change_ticket": enforce_ticket,
            "enforce_changelog_entry": enforce_changelog,
            "split_role_required": split_role_required,
            "split_role_paths": split_role_paths,
            "approval_freshness_required": freshness_required,
            "approval_granted_at_utc": approval_time.isoformat() if approval_time else "",
            "last_security_change_at_utc": security_change_time.isoformat() if security_change_time else "",
            "matched_competency_domains": matched_competency_domains,
            "missing_competency_domains": missing_competency_domains,
        },
    }
    out = evidence_root() / "security" / "review_policy_gate.json"
    write_json_report(out, report)
    print(f"REVIEW_POLICY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
