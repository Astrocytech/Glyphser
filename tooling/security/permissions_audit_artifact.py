#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

WORKFLOWS = ROOT / ".github" / "workflows"
PERM_INLINE_RE = re.compile(r"^\s*permissions:\s*(.+?)\s*$")
PERM_KEYVAL_RE = re.compile(r"^\s*([A-Za-z0-9_-]+):\s*(read|write|none)\s*$")


def _workflow_permissions(path: Path) -> dict[str, Any]:
    lines = path.read_text(encoding="utf-8").splitlines()
    inline: list[str] = []
    blocks: list[dict[str, str]] = []
    in_perm_block = False
    block_indent = 0
    current_block: dict[str, str] = {}

    for raw in lines:
        m_inline = PERM_INLINE_RE.match(raw)
        if m_inline and m_inline.group(1).strip() and m_inline.group(1).strip() != "":
            val = m_inline.group(1).strip()
            inline.append(val)
            in_perm_block = False
            current_block = {}
            continue

        if raw.strip() == "permissions:":
            in_perm_block = True
            block_indent = len(raw) - len(raw.lstrip(" "))
            current_block = {}
            continue

        if in_perm_block:
            indent = len(raw) - len(raw.lstrip(" "))
            if not raw.strip() or indent <= block_indent:
                if current_block:
                    blocks.append(current_block)
                in_perm_block = False
                current_block = {}
                continue
            m_kv = PERM_KEYVAL_RE.match(raw)
            if m_kv:
                current_block[m_kv.group(1)] = m_kv.group(2)

    if in_perm_block and current_block:
        blocks.append(current_block)

    return {"inline": inline, "blocks": blocks}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    workflows: list[dict[str, Any]] = []

    for wf in sorted(WORKFLOWS.glob("*.yml")):
        perms = _workflow_permissions(wf)
        if any(value.lower() == "write-all" for value in perms["inline"]):
            findings.append(f"workflow_permissions_write_all:{wf.name}")
        workflows.append({"workflow": wf.name, "permissions": perms})

    repo_scopes_env = os.environ.get("GLYPHSER_REPO_PERMISSION_SCOPES", "").strip()
    repo_scopes = [item.strip() for item in repo_scopes_env.split(",") if item.strip()] if repo_scopes_env else []

    report = {
        "status": "PASS" if not findings else "WARN",
        "findings": findings,
        "summary": {
            "generated_at_utc": datetime.now(UTC).isoformat(),
            "workflows_audited": len(workflows),
            "repo_permission_scopes_count": len(repo_scopes),
        },
        "metadata": {"gate": "permissions_audit_artifact", "periodic": True},
        "repo_permission_scopes": repo_scopes,
        "workflow_permissions": workflows,
    }

    out = evidence_root() / "security" / "permissions_audit_artifact.json"
    write_json_report(out, report)
    print(f"PERMISSIONS_AUDIT_ARTIFACT: {report['status']}")
    print(f"Report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
