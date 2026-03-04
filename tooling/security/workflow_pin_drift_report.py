#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

USES_RE = re.compile(r"^\s*(?:-\s*)?uses:\s*([^\s]+)\s*$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def main(argv: list[str] | None = None) -> int:
    _ = argv
    rows: list[dict[str, str | int | bool]] = []
    unpinned = 0
    for wf in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        rel = str(wf.relative_to(ROOT)).replace("\\", "/")
        for idx, line in enumerate(wf.read_text(encoding="utf-8").splitlines(), start=1):
            m = USES_RE.match(line)
            if not m:
                continue
            uses_ref = m.group(1)
            if uses_ref.startswith("./"):
                continue
            pinned = False
            if "@" in uses_ref:
                _a, ref = uses_ref.rsplit("@", 1)
                pinned = bool(SHA_RE.fullmatch(ref))
            if not pinned:
                unpinned += 1
            rows.append({"workflow": rel, "line": idx, "uses": uses_ref, "pinned": pinned})

    report = {
        "status": "PASS",
        "findings": [],
        "summary": {"action_references": len(rows), "unpinned_references": unpinned},
        "metadata": {"gate": "workflow_pin_drift_report"},
        "rows": rows,
    }
    out = evidence_root() / "security" / "workflow_pin_drift_report.json"
    write_json_report(out, report)
    sig = artifact_signing.sign_file(out, key=artifact_signing.current_key(strict=False))
    out.with_suffix(".json.sig").write_text(sig + "\n", encoding="utf-8")
    print("WORKFLOW_PIN_DRIFT_REPORT: PASS")
    print(f"Report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
