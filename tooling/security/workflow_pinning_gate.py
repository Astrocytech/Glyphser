#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TypedDict

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root
from tooling.security.report_io import write_json_report

USES_RE = re.compile(r"^\s*(?:-\s*)?uses:\s*([^\s]+)\s*$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
EXCEPTIONS_PATH = ROOT / "governance" / "security" / "workflow_pinning_exceptions.json"


class Finding(TypedDict):
    workflow: str
    line: int
    uses: str
    reason: str


def _parse_ts(text: str) -> datetime | None:
    if not isinstance(text, str) or not text.strip():
        return None
    normalized = text.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _load_exceptions(now_utc: datetime) -> tuple[set[tuple[str, str]], list[str], dict[str, int]]:
    active: set[tuple[str, str]] = set()
    findings: list[str] = []
    summary = {"configured_exceptions": 0, "active_exceptions": 0, "expired_exceptions": 0}
    if not EXCEPTIONS_PATH.exists():
        return active, findings, summary
    payload = json.loads(EXCEPTIONS_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        findings.append("workflow_pinning_exceptions_policy_invalid")
        return active, findings, summary

    raw = payload.get("exceptions", [])
    if not isinstance(raw, list):
        findings.append("workflow_pinning_exceptions_list_invalid")
        return active, findings, summary

    for item in raw:
        summary["configured_exceptions"] += 1
        if not isinstance(item, dict):
            findings.append("workflow_pinning_exception_entry_invalid")
            continue
        workflow = str(item.get("workflow", "")).strip()
        uses = str(item.get("uses", "")).strip()
        expires_text = str(item.get("expires_at_utc", "")).strip()
        if not workflow or not uses or not expires_text:
            findings.append("workflow_pinning_exception_missing_fields")
            continue
        expires = _parse_ts(expires_text)
        if expires is None:
            findings.append(f"workflow_pinning_exception_invalid_expiry:{workflow}:{uses}")
            continue
        if expires <= now_utc:
            summary["expired_exceptions"] += 1
            findings.append(f"workflow_pinning_exception_expired:{workflow}:{uses}")
            continue
        active.add((workflow, uses))
        summary["active_exceptions"] += 1
    return active, findings, summary


def _scan_workflow(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    rel = path.relative_to(ROOT).as_posix()
    for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        match = USES_RE.match(line)
        if not match:
            continue
        uses_ref = match.group(1)
        if uses_ref.startswith("./"):
            continue
        if "@" not in uses_ref:
            findings.append(
                {
                    "workflow": rel,
                    "line": idx,
                    "uses": uses_ref,
                    "reason": "missing_ref",
                }
            )
            continue
        _action, ref = uses_ref.rsplit("@", 1)
        if not SHA_RE.fullmatch(ref):
            findings.append(
                {
                    "workflow": rel,
                    "line": idx,
                    "uses": uses_ref,
                    "reason": "ref_not_pinned_to_sha",
                }
            )
    return findings


def main() -> int:
    now_utc = datetime.now(UTC)
    active_exceptions, policy_findings, exception_summary = _load_exceptions(now_utc)
    workflows = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
    findings: list[Finding] = []
    suppressed: list[Finding] = []
    for workflow in workflows:
        for finding in _scan_workflow(workflow):
            key = (finding["workflow"], finding["uses"])
            if key in active_exceptions:
                suppressed.append(finding)
                continue
            findings.append(finding)

    status = "PASS" if not findings and not policy_findings else "FAIL"
    payload: dict[str, object] = {
        "status": status,
        "workflow_count": len(workflows),
        "finding_count": len(findings),
        "policy_finding_count": len(policy_findings),
        "findings": findings,
        "policy_findings": policy_findings,
        "suppressed_findings": suppressed,
        "summary": exception_summary,
        "metadata": {"gate": "workflow_pinning_gate", "evaluated_at_utc": now_utc.isoformat()},
    }
    out = evidence_root() / "security" / "workflow_pinning.json"
    write_json_report(out, payload)

    print(f"WORKFLOW_PINNING_GATE: {status}")
    print(f"Report: {out}")
    if findings:
        for finding in findings[:25]:
            print(f"{finding['workflow']}:{finding['line']}:{finding['uses']}:{finding['reason']}")
    if policy_findings:
        for finding in policy_findings[:25]:
            print(f"policy:{finding}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
