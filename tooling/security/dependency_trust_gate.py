#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from tooling.lib.path_config import evidence_root
from tooling.security.stage_s_policy import load_stage_s_policy

ROOT = Path(__file__).resolve().parents[2]
USES_RE = re.compile(r"^\s*(?:-\s*)?uses:\s*([^\s]+)\s*$")


def _owner(ref: str) -> str:
    if ref.startswith("./"):
        return "local"
    owner = ref.split("/", 1)[0]
    return owner.lower()


def main(argv: list[str] | None = None) -> int:
    _ = argv
    cfg = load_stage_s_policy().get("dependency_trust", {})
    allowed = {x.lower() for x in cfg.get("allowed_action_owners", []) if isinstance(x, str)}
    allow_local = bool(cfg.get("allow_local_actions", True))

    findings: list[str] = []
    checked: list[str] = []
    for wf in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        for line in wf.read_text(encoding="utf-8").splitlines():
            m = USES_RE.match(line)
            if not m:
                continue
            ref = m.group(1)
            checked.append(ref)
            owner = _owner(ref)
            if owner == "local" and allow_local:
                continue
            if owner not in allowed:
                findings.append(f"untrusted_action_owner:{wf.name}:{owner}:{ref}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"checked_uses_entries": len(checked), "allowed_owners": sorted(allowed)},
        "metadata": {"gate": "dependency_trust_gate"},
    }
    out = evidence_root() / "security" / "dependency_trust_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"DEPENDENCY_TRUST_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
