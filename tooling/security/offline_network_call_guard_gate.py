#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY = ROOT / "governance" / "security" / "network_egress_policy.json"
SECURITY_DIR = ROOT / "tooling" / "security"

NETWORK_PATTERNS = {
    "requests": re.compile(r"\bimport\s+requests\b|\bfrom\s+requests\s+import\b"),
    "httpx": re.compile(r"\bimport\s+httpx\b|\bfrom\s+httpx\s+import\b"),
    "urllib": re.compile(r"\burllib\.request\b|\bfrom\s+urllib\s+import\b"),
    "socket": re.compile(r"\bimport\s+socket\b|\bfrom\s+socket\s+import\b"),
    "curl_wget": re.compile(r"\bcurl\b|\bwget\b"),
    "http_url": re.compile(r"https?://"),
}


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _candidate_scripts() -> list[Path]:
    out: list[Path] = []
    for path in sorted(SECURITY_DIR.glob("*.py")):
        name = path.name
        if "offline" in name or "verify" in name:
            out.append(path)
    return out


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = _load_json(POLICY)
    allowlisted = {
        item.strip()
        for item in policy.get("network_required_gates", [])
        if isinstance(item, str) and item.strip().startswith("tooling/security/")
    }

    findings: list[str] = []
    scanned: dict[str, list[str]] = {}
    for script in _candidate_scripts():
        rel = str(script.relative_to(ROOT)).replace("\\", "/")
        if rel in allowlisted:
            continue
        text = script.read_text(encoding="utf-8")
        hits = [label for label, pattern in NETWORK_PATTERNS.items() if pattern.search(text)]
        scanned[rel] = hits
        for hit in hits:
            findings.append(f"offline_script_network_pattern:{rel}:{hit}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "offline_scripts_scanned": len(scanned),
            "scripts_with_network_patterns": len([k for k, v in scanned.items() if v]),
            "allowlisted_network_required_scripts": sorted(allowlisted),
        },
        "metadata": {"gate": "offline_network_call_guard_gate"},
        "scanned_scripts": scanned,
    }
    out = evidence_root() / "security" / "offline_network_call_guard_gate.json"
    write_json_report(out, report)
    print(f"OFFLINE_NETWORK_CALL_GUARD_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
