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
load_policy = importlib.import_module("tooling.security.advanced_policy").load_policy
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

TARGET_DIRS = [ROOT / "runtime", ROOT / "tooling", ROOT / "governance" / "security"]


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = load_policy()
    forbidden = [x.lower() for x in policy.get("forbidden_algorithms", []) if isinstance(x, str)]
    findings: list[str] = []
    hits: list[str] = []

    for base in sorted(TARGET_DIRS):
        for path in sorted(base.rglob("*.py")):
            text = path.read_text(encoding="utf-8")
            lowered = text.lower()
            for algo in forbidden:
                needle = f"hashlib.{algo}"
                if needle in lowered:
                    rel = str(path.relative_to(ROOT)).replace("\\", "/")
                    hits.append(f"{rel}:{needle}")
                    findings.append(f"forbidden_algorithm_used:{rel}:{algo}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"forbidden_algorithms": forbidden, "hits": hits},
        "metadata": {"gate": "crypto_algorithm_policy_gate"},
    }
    out = evidence_root() / "security" / "crypto_algorithm_policy_gate.json"
    write_json_report(out, report)
    print(f"CRYPTO_ALGORITHM_POLICY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
