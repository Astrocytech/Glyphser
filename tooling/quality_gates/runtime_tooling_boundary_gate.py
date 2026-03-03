#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.quality_gates.telemetry import emit_gate_trace

RUNTIME_DIR = ROOT / "runtime"
OUT = ROOT / "evidence" / "gates" / "quality" / "runtime_tooling_boundary.json"

IMPORT_RE = re.compile(r"^\s*(from\s+tooling(\.|\s)|import\s+tooling(\.|\s|$))")


def evaluate() -> dict:
    findings: list[str] = []
    for py in sorted(RUNTIME_DIR.rglob("*.py")):
        rel = str(py.relative_to(ROOT)).replace("\\", "/")
        for idx, line in enumerate(py.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
            if IMPORT_RE.search(line):
                findings.append(f"runtime_imports_tooling:{rel}:{idx}")

    payload = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "rule": "runtime_must_not_import_tooling",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    emit_gate_trace(ROOT, "runtime_tooling_boundary", payload)
    return payload


def main() -> int:
    report = evaluate()
    if report["status"] == "PASS":
        print("RUNTIME_TOOLING_BOUNDARY_GATE: PASS")
        return 0
    print("RUNTIME_TOOLING_BOUNDARY_GATE: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
