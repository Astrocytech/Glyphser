#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from tooling.lib.path_config import evidence_root
from tooling.security.advanced_policy import load_policy

URL_RE = re.compile(r"https://([A-Za-z0-9_.-]+)")

ROOT = Path(__file__).resolve().parents[2]



def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = load_policy()
    allowed = {x for x in policy.get("allowed_egress_domains", []) if isinstance(x, str)}
    findings: list[str] = []
    seen: dict[str, list[str]] = {}

    for wf in (ROOT / ".github" / "workflows").glob("*.yml"):
        text = wf.read_text(encoding="utf-8")
        hosts = sorted(set(URL_RE.findall(text)))
        if not hosts:
            continue
        seen[wf.name] = hosts
        for host in hosts:
            if host not in allowed:
                findings.append(f"unapproved_egress_domain:{wf.name}:{host}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"allowed_domains": sorted(allowed), "workflow_domains": seen},
        "metadata": {"gate": "egress_policy_gate"},
    }
    out = evidence_root() / "security" / "egress_policy_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"EGRESS_POLICY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
