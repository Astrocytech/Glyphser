#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
subprocess_policy = importlib.import_module("tooling.security.subprocess_policy")
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _collect_callsites() -> list[str]:
    callsites: list[str] = []
    for path in sorted((ROOT / "tooling" / "security").glob("*.py")):
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if "run_checked(" in line:
                callsites.append(f"{rel}:{idx}")
    return callsites


def main(argv: list[str] | None = None) -> int:
    _ = argv
    prefixes = [list(prefix) for prefix in sorted(subprocess_policy._ALLOWED_PREFIXES)]  # noqa: SLF001
    callsites = _collect_callsites()
    report = {
        "status": "PASS",
        "findings": [],
        "summary": {
            "allowed_prefixes": len(prefixes),
            "callsites": len(callsites),
        },
        "metadata": {"gate": "subprocess_allowlist_report"},
        "allowed_prefixes": prefixes,
        "callsites": callsites,
    }
    out = evidence_root() / "security" / "subprocess_allowlist_report.json"
    write_json_report(out, report)
    print("SUBPROCESS_ALLOWLIST_REPORT: PASS")
    print(f"Report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
