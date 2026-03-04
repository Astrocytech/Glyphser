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
load_stage_s_policy = importlib.import_module("tooling.security.stage_s_policy").load_stage_s_policy
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def main(argv: list[str] | None = None) -> int:
    _ = argv
    cfg = load_stage_s_policy().get("transparency_log", {})
    log_path = ROOT / str(cfg.get("log_path", "evidence/security/transparency_log.json"))
    payload = json.loads(log_path.read_text(encoding="utf-8")) if log_path.exists() else {}
    entries = payload.get("entries", []) if isinstance(payload, dict) else []

    findings: list[str] = []
    if not isinstance(entries, list) or not entries:
        findings.append("missing_transparency_entries")
        entries = []

    for i in range(1, len(entries)):
        prev = entries[i - 1]
        cur = entries[i]
        if not isinstance(prev, dict) or not isinstance(cur, dict):
            findings.append(f"invalid_entry:{i}")
            continue
        if str(cur.get("previous_root", "")) != str(prev.get("root", "")):
            findings.append(f"broken_chain:{i}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"entries": len(entries)},
        "metadata": {"gate": "transparency_log_gate"},
    }
    out = evidence_root() / "security" / "transparency_log_gate.json"
    write_json_report(out, report)
    print(f"TRANSPARENCY_LOG_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
