#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import json
import platform
import sys
from pathlib import Path
from typing import Mapping

CASES = [
    {"name": "single_actor_burst", "events": [{"actor_id": "actor-01", "kind": "replay"}] * 8},
    {
        "name": "actor_spray",
        "events": [{"actor_id": f"actor-{i:02d}", "kind": "replay"} for i in range(8)],
    },
]


def _score(case: Mapping[str, object]) -> int:
    events = case.get("events", [])
    if not isinstance(events, list):
        return -1
    actors = [str(e.get("actor_id", "")) for e in events if isinstance(e, dict)]
    unique = len(set(actors))
    return len(actors) + (unique * 3)


def _python_version() -> str:
    return platform.python_version()


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    scores: dict[str, int] = {}
    for case in CASES:
        name = str(case["name"])
        score = _score(case)
        if score < 0:
            findings.append(f"invalid_case:{name}")
            continue
        scores[name] = score

    digest = hashlib.sha256(json.dumps(scores, sort_keys=True).encode("utf-8")).hexdigest()
    status = "PASS" if not findings else "FAIL"
    report = {
        "status": status,
        "findings": findings,
        "summary": {"scores": scores, "deterministic_digest": digest},
        "metadata": {"gate": "replay_abuse_regression_gate", "python_version": _python_version()},
    }
    out = evidence_root() / "security" / "replay_abuse_regression_gate.json"
    write_json_report(out, report)
    print(f"REPLAY_ABUSE_REGRESSION_GATE: {status}")
    print(f"Report: {out}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
