#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import stat
import sys
from pathlib import Path

from tooling.lib.path_config import evidence_root


def _mode(path: Path) -> int:
    return stat.S_IMODE(path.stat().st_mode)


ROOT = Path(__file__).resolve().parents[2]


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
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"FILE_PERMISSION_MATRIX_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
