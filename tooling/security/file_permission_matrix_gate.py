#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _mode(path: Path) -> int:
    return stat.S_IMODE(path.stat().st_mode)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    targets = [
        ROOT / "evidence" / "security" / "sbom.json",
        ROOT / "evidence" / "security" / "build_provenance.json",
        ROOT / "governance" / "security" / "review_policy.json",
    ]
    findings: list[str] = []
    matrix: dict[str, object] = {}
    for path in targets:
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        if not path.exists():
            findings.append(f"missing_target:{rel}")
            continue
        mode = _mode(path)
        matrix[rel] = {"mode": oct(mode), "platform": os.name}
        if mode & 0o022:
            findings.append(f"group_or_world_writable:{rel}:{oct(mode)}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"matrix": matrix},
        "metadata": {"gate": "file_permission_matrix_gate"},
    }
    out = evidence_root() / "security" / "file_permission_matrix_gate.json"
    write_json_report(out, report)
    print(f"FILE_PERMISSION_MATRIX_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
