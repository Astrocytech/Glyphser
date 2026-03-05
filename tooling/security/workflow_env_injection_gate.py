#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root
from tooling.security.report_io import write_json_report

POLICY = ROOT / "governance" / "security" / "workflow_env_var_policy.json"
WORKFLOWS = ROOT / ".github" / "workflows"
ENV_KEY_RE = re.compile(r"^\s*([A-Z][A-Z0-9_]*):\s*")


def _extract_env_keys(text: str) -> set[str]:
    keys: set[str] = set()
    in_env = False
    env_indent = 0
    for raw in text.splitlines():
        line = raw.rstrip("\n")
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        if stripped == "env:":
            in_env = True
            env_indent = indent
            continue
        if in_env and indent <= env_indent:
            in_env = False
        if not in_env:
            continue
        match = ENV_KEY_RE.match(line)
        if match:
            keys.add(match.group(1))
    return keys


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    payload = json.loads(POLICY.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("workflow env policy must be a JSON object")

    globs = [str(x).strip() for x in payload.get("workflow_file_globs", []) if str(x).strip()]
    patterns = [re.compile(str(x)) for x in payload.get("allowed_env_var_patterns", []) if str(x).strip()]
    if not globs or not patterns:
        raise ValueError("workflow env policy missing globs or allowed_env_var_patterns")

    all_keys: dict[str, list[str]] = {}
    for glob in globs:
        for path in sorted(WORKFLOWS.glob(glob)):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            keys = sorted(_extract_env_keys(text))
            if not keys:
                continue
            rel = str(path.relative_to(ROOT)).replace("\\", "/")
            all_keys[rel] = keys
            for key in keys:
                if not any(pattern.fullmatch(key) for pattern in patterns):
                    findings.append(f"unexpected_env_var:{rel}:{key}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "workflows_scanned": len(all_keys),
            "distinct_env_keys": sorted({key for keys in all_keys.values() for key in keys}),
        },
        "metadata": {"gate": "workflow_env_injection_gate", "workflow_env_keys": all_keys},
    }
    out = evidence_root() / "security" / "workflow_env_injection_gate.json"
    write_json_report(out, report)
    print(f"WORKFLOW_ENV_INJECTION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
