#!/usr/bin/env python3
from __future__ import annotations

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

POLICY = ROOT / "governance" / "security" / "shared_security_template_compatibility.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not POLICY.exists():
        findings.append("missing_shared_security_template_compatibility_policy")
        policy: dict[str, Any] = {}
    else:
        try:
            policy = _load_json(POLICY)
        except Exception:
            policy = {}
            findings.append("invalid_shared_security_template_compatibility_policy")

    templates = policy.get("templates", []) if isinstance(policy, dict) else []
    if not isinstance(templates, list):
        templates = []
        findings.append("invalid_templates_list")

    checked = 0
    for item in templates:
        if not isinstance(item, dict):
            findings.append("invalid_template_entry")
            continue
        rel = str(item.get("path", "")).strip()
        markers = item.get("required_markers", [])
        if not rel:
            findings.append("missing_template_path")
            continue
        path = ROOT / rel
        if not path.exists():
            findings.append(f"missing_template:{rel}")
            continue
        text = path.read_text(encoding="utf-8")
        checked += 1
        if not isinstance(markers, list):
            findings.append(f"invalid_required_markers:{rel}")
            continue
        for marker in markers:
            if not isinstance(marker, str) or not marker.strip():
                findings.append(f"invalid_marker:{rel}")
                continue
            if marker not in text:
                findings.append(f"missing_marker:{rel}:{marker}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"templates_declared": len(templates), "templates_checked": checked},
        "metadata": {"gate": "shared_security_template_compatibility_gate"},
    }
    out = evidence_root() / "security" / "shared_security_template_compatibility_gate.json"
    write_json_report(out, report)
    print(f"SHARED_SECURITY_TEMPLATE_COMPATIBILITY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
