#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY = ROOT / "governance" / "security" / "docs_security_command_policy.json"


def _load_policy(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"invalid policy json object: {path}")
    return payload


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    scanned_files: set[str] = set()
    forbidden_hits = 0
    deprecated_hits = 0

    policy = _load_policy(POLICY)
    scan_globs = [str(item) for item in policy.get("scan_globs", []) if isinstance(item, str) and item.strip()]
    forbidden_patterns = [row for row in policy.get("forbidden_patterns", []) if isinstance(row, dict)]
    deprecated_guidance = [row for row in policy.get("deprecated_guidance", []) if isinstance(row, dict)]

    files_to_scan: set[Path] = set()
    for glob in scan_globs:
        files_to_scan.update(path for path in ROOT.glob(glob) if path.is_file())

    for path in sorted(files_to_scan):
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        scanned_files.add(rel)
        text = path.read_text(encoding="utf-8", errors="ignore")

        for row in forbidden_patterns:
            rid = str(row.get("id", "")).strip()
            pattern = str(row.get("pattern", "")).strip()
            if not rid or not pattern:
                continue
            if re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE):
                forbidden_hits += 1
                findings.append(f"forbidden_security_command_pattern:{rid}:{rel}")

        for row in deprecated_guidance:
            rid = str(row.get("id", "")).strip()
            fragment = str(row.get("contains", "")).strip()
            if not rid or not fragment:
                continue
            if fragment in text:
                deprecated_hits += 1
                findings.append(f"outdated_security_guidance:{rid}:{rel}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": sorted(set(findings)),
        "summary": {
            "files_scanned": len(scanned_files),
            "forbidden_pattern_hits": forbidden_hits,
            "deprecated_guidance_hits": deprecated_hits,
        },
        "metadata": {
            "gate": "docs_security_command_guard_gate",
            "policy_path": str(POLICY.relative_to(ROOT)).replace("\\", "/"),
        },
    }
    out = evidence_root() / "security" / "docs_security_command_guard_gate.json"
    write_json_report(out, report)
    print(f"DOCS_SECURITY_COMMAND_GUARD_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
