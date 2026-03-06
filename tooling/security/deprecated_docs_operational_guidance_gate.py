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
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY = ROOT / "governance" / "security" / "deprecated_docs_policy.json"


def _load_policy(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    if not POLICY.exists():
        findings.append("missing_deprecated_docs_policy")
        policy = {}
    else:
        policy = _load_policy(POLICY)

    deprecated_docs = [str(p).strip() for p in policy.get("deprecated_docs", []) if str(p).strip()]
    required_markers = [str(m).strip() for m in policy.get("required_markers", []) if str(m).strip()]
    operational_docs = [str(p).strip() for p in policy.get("operational_guidance_docs", []) if str(p).strip()]

    if not deprecated_docs:
        findings.append("missing_deprecated_docs_configuration")
    if not required_markers:
        findings.append("missing_required_deprecated_markers")

    for rel in deprecated_docs:
        dep = ROOT / rel
        if not dep.exists():
            findings.append(f"missing_deprecated_doc:{rel}")
            continue
        text = dep.read_text(encoding="utf-8", errors="ignore")
        if not all(marker in text for marker in required_markers):
            findings.append(f"deprecated_doc_missing_marker:{rel}")

    for rel in operational_docs:
        op = ROOT / rel
        if not op.exists():
            findings.append(f"missing_operational_guidance_doc:{rel}")
            continue
        text = op.read_text(encoding="utf-8", errors="ignore")
        for dep_rel in deprecated_docs:
            if dep_rel in text:
                findings.append(f"deprecated_doc_referenced_in_operational_guidance:{rel}:{dep_rel}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "deprecated_docs": len(deprecated_docs),
            "operational_guidance_docs": len(operational_docs),
        },
        "metadata": {
            "gate": "deprecated_docs_operational_guidance_gate",
            "policy_path": str(POLICY.relative_to(ROOT)).replace("\\", "/"),
        },
    }
    out = evidence_root() / "security" / "deprecated_docs_operational_guidance_gate.json"
    write_json_report(out, report)
    print(f"DEPRECATED_DOCS_OPERATIONAL_GUIDANCE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
