#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from tooling.lib.path_config import evidence_root
from tooling.security.advanced_policy import load_policy

ROOT = Path(__file__).resolve().parents[2]

TARGET_DIRS = [ROOT / "runtime", ROOT / "tooling", ROOT / "governance" / "security"]


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = load_policy()
    forbidden = [x.lower() for x in policy.get("forbidden_algorithms", []) if isinstance(x, str)]
    findings: list[str] = []
    hits: list[str] = []

    for base in TARGET_DIRS:
        for path in base.rglob("*.py"):
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
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CRYPTO_ALGORITHM_POLICY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
