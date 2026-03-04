#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import TypedDict

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root

USES_RE = re.compile(r"^\s*-\s*uses:\s*([^\s]+)\s*$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
EXEMPT_USES_REFS = {
    "actions/download-artifact@v4",
    "pypa/gh-action-pypi-publish@release/v1",
}


class Finding(TypedDict):
    workflow: str
    line: int
    uses: str
    reason: str


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
        if uses_ref in EXEMPT_USES_REFS:
            continue
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
    workflows = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
    findings: list[Finding] = []
    for workflow in workflows:
        findings.extend(_scan_workflow(workflow))

    status = "PASS" if not findings else "FAIL"
    payload: dict[str, object] = {
        "status": status,
        "workflow_count": len(workflows),
        "finding_count": len(findings),
        "findings": findings,
        "exempt_uses_refs": sorted(EXEMPT_USES_REFS),
    }
    out = evidence_root() / "security" / "workflow_pinning.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"WORKFLOW_PINNING_GATE: {status}")
    print(f"Report: {out}")
    if findings:
        for finding in findings[:25]:
            print(f"{finding['workflow']}:{finding['line']}:{finding['uses']}:{finding['reason']}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
