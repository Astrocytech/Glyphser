#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from tooling.lib.path_config import evidence_root
from tooling.security.advanced_policy import load_policy


def _workflow_names() -> list[str]:
    names: list[str] = []
    for path in (ROOT / ".github" / "workflows").glob("*.yml"):
        names.append(path.name)
    return sorted(names)

ROOT = Path(__file__).resolve().parents[2]



def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = load_policy()
    allowed = {x for x in policy.get("allowed_security_workflows", []) if isinstance(x, str)}
    required_files = [x for x in policy.get("security_workflow_evidence_required", []) if isinstance(x, str)]

    findings: list[str] = []
    present = _workflow_names()
    missing_workflows = sorted(x for x in allowed if x not in set(present))
    for wf in missing_workflows:
        findings.append(f"missing_workflow:{wf}")

    ev = evidence_root() / "security"
    for rel in required_files:
        target = ev / rel
        if not target.exists():
            findings.append(f"missing_evidence:{rel}")
            continue
        if target.suffix == ".json":
            try:
                payload = json.loads(target.read_text(encoding="utf-8"))
            except Exception:
                findings.append(f"invalid_json:{rel}")
                continue
            if not isinstance(payload, dict) or "status" not in payload:
                findings.append(f"invalid_schema:{rel}")

    status = "PASS" if not findings else "FAIL"
    report = {
        "status": status,
        "findings": findings,
        "summary": {
            "required_workflows": sorted(allowed),
            "required_evidence_files": required_files,
            "evidence_root": str(ev),
        },
        "metadata": {"gate": "security_workflow_evidence_bundle_gate"},
    }
    out = ev / "security_workflow_evidence_bundle_gate.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"SECURITY_WORKFLOW_EVIDENCE_BUNDLE_GATE: {status}")
    print(f"Report: {out}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
