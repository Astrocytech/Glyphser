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

DEPRECATED_SNIPPETS = (
    "python -m semgrep",
    "python3 -m semgrep",
    "pysemgrep",
)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    scanned = 0
    for wf in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        scanned += 1
        rel = str(wf.relative_to(ROOT)).replace("\\", "/")
        for idx, line in enumerate(wf.read_text(encoding="utf-8").splitlines(), start=1):
            for snippet in DEPRECATED_SNIPPETS:
                if snippet in line:
                    findings.append(f"deprecated_invocation:{rel}:{idx}:{snippet}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"scanned_workflows": scanned, "deprecated_patterns": list(DEPRECATED_SNIPPETS)},
        "metadata": {"gate": "workflow_deprecated_invocation_gate"},
    }
    out = evidence_root() / "security" / "workflow_deprecated_invocation_gate.json"
    write_json_report(out, report)
    print(f"WORKFLOW_DEPRECATED_INVOCATION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
