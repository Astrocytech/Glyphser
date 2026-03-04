#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path

URL_RE = re.compile(r"https://([A-Za-z0-9_.-]+)")

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
load_policy = importlib.import_module("tooling.security.advanced_policy").load_policy
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = load_policy()
    allowed = {x for x in policy.get("allowed_egress_domains", []) if isinstance(x, str)}
    findings: list[str] = []
    seen: dict[str, list[str]] = {}

    for wf in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
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
    write_json_report(out, report)
    print(f"EGRESS_POLICY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
