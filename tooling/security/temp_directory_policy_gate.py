#!/usr/bin/env python3
from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

SCAN_DIRS = [ROOT / "tooling" / "security", ROOT / "runtime" / "glyphser" / "security"]
FORBIDDEN_PATTERNS = [
    (re.compile(r"\btempfile\.mktemp\s*\("), "forbidden_tempfile_mktemp"),
    (re.compile(r"\bNamedTemporaryFile\s*\([^)]*delete\s*=\s*False"), "forbidden_named_temporary_file_delete_false"),
]
TEMP_ALLOC_PATTERNS = [re.compile(r"\btempfile\.mkstemp\s*\("), re.compile(r"\btempfile\.mkdtemp\s*\(")]
CLEANUP_HINTS = ("TemporaryDirectory(", ".unlink(", "os.unlink(", "shutil.rmtree(", "cleanup(")


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    scanned_files = 0
    temp_alloc_files = 0

    for base in SCAN_DIRS:
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.py")):
            scanned_files += 1
            rel = str(path.relative_to(ROOT)).replace("\\", "/")
            text = path.read_text(encoding="utf-8")

            for pattern, finding in FORBIDDEN_PATTERNS:
                if pattern.search(text):
                    findings.append(f"{finding}:{rel}")

            alloc_used = any(pattern.search(text) for pattern in TEMP_ALLOC_PATTERNS)
            if alloc_used:
                temp_alloc_files += 1
                if not any(hint in text for hint in CLEANUP_HINTS):
                    findings.append(f"tempfile_allocation_without_cleanup_hint:{rel}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"scanned_files": scanned_files, "files_with_temp_allocations": temp_alloc_files},
        "metadata": {"gate": "temp_directory_policy_gate"},
    }
    out = evidence_root() / "security" / "temp_directory_policy_gate.json"
    write_json_report(out, report)
    print(f"TEMP_DIRECTORY_POLICY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
