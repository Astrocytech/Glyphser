#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    scanned = 0
    for base in sorted([evidence_root() / "security", ROOT / "governance" / "security"]):
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            scanned += 1
            mode = stat.S_IMODE(path.stat().st_mode)
            if mode & 0o002:
                findings.append(f"world_writable:{path}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"scanned_files": scanned},
        "metadata": {"gate": "file_permissions_gate"},
    }
    out = evidence_root() / "security" / "file_permissions_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"FILE_PERMISSIONS_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
