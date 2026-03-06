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

POLICY = ROOT / "governance" / "security" / "docs_snippet_pinning_policy.json"
USES_REF = re.compile(r"uses:\s*([^\s@]+)@([^\s]+)")
SHA40 = re.compile(r"^[0-9a-f]{40}$")


def _load_policy(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"invalid policy json object: {path}")
    return payload


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    scanned_files: set[str] = set()
    policy = _load_policy(POLICY)
    scan_globs = [str(item) for item in policy.get("scan_globs", []) if isinstance(item, str) and item.strip()]
    enforce = bool(policy.get("enforce_action_sha_pinning", True))

    files_to_scan: set[Path] = set()
    for glob in scan_globs:
        files_to_scan.update(path for path in ROOT.glob(glob) if path.is_file())

    for path in sorted(files_to_scan):
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        scanned_files.add(rel)
        text = path.read_text(encoding="utf-8", errors="ignore")
        if not enforce:
            continue
        for action, ref in USES_REF.findall(text):
            action = action.strip()
            ref = ref.strip()
            if action.startswith("./") or action.startswith("docker://"):
                continue
            if ref.startswith("${{"):
                findings.append(f"non_immutable_action_ref:{rel}:{action}@{ref}")
                continue
            if not SHA40.fullmatch(ref.lower()):
                findings.append(f"unpinned_action_ref:{rel}:{action}@{ref}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": sorted(set(findings)),
        "summary": {
            "files_scanned": len(scanned_files),
            "action_pin_violations": len(findings),
        },
        "metadata": {
            "gate": "docs_snippet_pinning_gate",
            "policy_path": str(POLICY.relative_to(ROOT)).replace("\\", "/"),
        },
    }
    out = evidence_root() / "security" / "docs_snippet_pinning_gate.json"
    write_json_report(out, report)
    print(f"DOCS_SNIPPET_PINNING_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
