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
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    findings: list[str] = []
    scanned = 0
    newline_terminated = 0

    for path in sorted(sec.glob("*.json")):
        scanned += 1
        rel = str(path.relative_to(evidence_root())).replace("\\", "/")
        raw = path.read_bytes()
        if raw.endswith(b"\n"):
            newline_terminated += 1
        else:
            findings.append(f"missing_trailing_newline:{rel}")
        try:
            json.loads(raw.decode("utf-8"))
        except Exception:
            findings.append(f"invalid_json:{rel}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "scanned_files": scanned,
            "newline_terminated": newline_terminated,
            "newline_termination_pct": round((newline_terminated / scanned * 100.0), 2) if scanned else 100.0,
        },
        "metadata": {"gate": "security_evidence_corruption_gate"},
    }
    out = sec / "security_evidence_corruption_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_EVIDENCE_CORRUPTION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
