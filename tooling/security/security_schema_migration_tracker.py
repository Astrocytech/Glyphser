#!/usr/bin/env python3
from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def main(argv: list[str] | None = None) -> int:
    _ = argv
    security_dir = ROOT / "tooling" / "security"
    migrated: list[str] = []
    legacy: list[str] = []

    for path in sorted(security_dir.glob("*_gate.py")):
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        text = path.read_text(encoding="utf-8")
        if "write_json_report(" in text:
            migrated.append(rel)
        else:
            legacy.append(rel)

    report = {
        "status": "PASS",
        "findings": [],
        "summary": {
            "total_gate_scripts": len(migrated) + len(legacy),
            "migrated_count": len(migrated),
            "legacy_count": len(legacy),
            "migration_pct": round((len(migrated) / (len(migrated) + len(legacy)) * 100.0), 2)
            if migrated or legacy
            else 100.0,
        },
        "metadata": {"gate": "security_schema_migration_tracker"},
        "migrated": migrated,
        "legacy": legacy,
    }
    out = evidence_root() / "security" / "security_schema_migration_tracker.json"
    write_json_report(out, report)
    print("SECURITY_SCHEMA_MIGRATION_TRACKER: PASS")
    print(f"Report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
