#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import stat
import sys
from fnmatch import fnmatch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
OWNER_ONLY_GLOBS = (
    "abuse_telemetry.json",
    "runtime_api_state.json",
    "security_events.jsonl",
)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    scanned = 0
    scanned_symlinks = 0
    scanned_hardlinks = 0

    for base in sorted([evidence_root() / "security", ROOT / "governance" / "security"]):
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_symlink():
                scanned_symlinks += 1
                findings.append(f"symlink_disallowed:{path}")
                continue
            if not path.is_file():
                continue

            scanned += 1
            st = path.stat()
            mode = stat.S_IMODE(st.st_mode)
            if mode & 0o002:
                findings.append(f"world_writable:{path}")
            if st.st_nlink > 1:
                scanned_hardlinks += 1
                findings.append(f"hardlink_detected:{path}:nlink={st.st_nlink}")

            if any(fnmatch(path.name, pat) for pat in OWNER_ONLY_GLOBS):
                if mode & (stat.S_IRWXG | stat.S_IRWXO):
                    findings.append(f"sensitive_not_owner_only:{path}:mode={oct(mode)}")

            if path.parent == evidence_root() / "security" and os.access(path, os.W_OK) and not os.access(path, os.R_OK):
                findings.append(f"write_only_artifact:{path}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "scanned_files": scanned,
            "scanned_symlinks": scanned_symlinks,
            "scanned_hardlinks": scanned_hardlinks,
            "owner_only_globs": list(OWNER_ONLY_GLOBS),
        },
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
