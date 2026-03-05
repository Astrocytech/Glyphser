#!/usr/bin/env python3
from __future__ import annotations

import glob
import hashlib
import importlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report
load_stage_s_policy = importlib.import_module("tooling.security.stage_s_policy").load_stage_s_policy


def _walk(obj: Any) -> list[str]:
    if isinstance(obj, dict):
        values: list[str] = []
        for v in obj.values():
            values.extend(_walk(v))
        return values
    if isinstance(obj, list):
        items: list[str] = []
        for v in obj:
            items.extend(_walk(v))
        return items
    if isinstance(obj, str):
        return [obj]
    return []


def _redaction(secret: str) -> str:
    return "REDACTED[sha256:" + hashlib.sha256(secret.encode("utf-8")).hexdigest() + "]"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    cfg = load_stage_s_policy().get("redaction", {})
    forbidden = [x for x in cfg.get("forbidden_literals", []) if isinstance(x, str)]
    prefix = str(cfg.get("allowed_redaction_prefix", "REDACTED[sha256:"))
    scan_glob = str(cfg.get("scan_glob", "evidence/security/*.json"))

    findings: list[str] = []
    redactions: dict[str, str] = {}
    for path_s in sorted(glob.glob(str(ROOT / scan_glob))):
        path = Path(path_s)
        payload: Any | None = None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            rel = str(path.relative_to(ROOT)).replace("\\", "/")
            findings.append(f"unreadable_or_invalid_json:{rel}:{type(exc).__name__}")
        if payload is None:
            continue
        strings = _walk(payload)
        for literal in forbidden:
            for s in strings:
                if literal in s:
                    if s.startswith(prefix):
                        continue
                    rel = str(path.relative_to(ROOT)).replace("\\", "/")
                    findings.append(f"unredacted_literal:{rel}:{literal}")
                    redactions[literal] = _redaction(literal)

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"deterministic_redactions": redactions},
        "metadata": {"gate": "deterministic_redaction_gate"},
    }
    out = evidence_root() / "security" / "deterministic_redaction_gate.json"
    write_json_report(out, report)
    print(f"DETERMINISTIC_REDACTION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
