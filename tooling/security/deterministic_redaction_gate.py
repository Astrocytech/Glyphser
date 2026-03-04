#!/usr/bin/env python3
from __future__ import annotations

import glob
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from tooling.lib.path_config import evidence_root
from tooling.security.stage_s_policy import load_stage_s_policy

ROOT = Path(__file__).resolve().parents[2]


def _walk(obj: Any) -> list[str]:
    if isinstance(obj, dict):
        out: list[str] = []
        for v in obj.values():
            out.extend(_walk(v))
        return out
    if isinstance(obj, list):
        out: list[str] = []
        for v in obj:
            out.extend(_walk(v))
        return out
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
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"DETERMINISTIC_REDACTION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
