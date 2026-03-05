#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    events: list[str] = []

    promotion = _load_json(sec / "promotion_policy_gate.json")
    if bool(((promotion.get("summary") or {}) if isinstance(promotion.get("summary"), dict) else {}).get("override_applied")):
        events.append("promotion_signed_override_applied")

    provenance = _load_json(sec / "key_provenance_continuity_gate.json")
    findings = provenance.get("findings", [])
    if isinstance(findings, list):
        for item in findings:
            if isinstance(item, str) and item.startswith("fallback_signing_used:"):
                events.append(item)

    if os.environ.get("GLYPHSER_ALLOW_RISKY_RUNTIME_DEFAULTS", "").strip().lower() in {"1", "true", "yes", "on"}:
        events.append("runtime_api_risky_defaults_override_enabled")

    report = {
        "status": "WARN" if events else "PASS",
        "findings": events,
        "summary": {"degraded_mode_events": len(events)},
        "metadata": {"gate": "degraded_mode_evidence", "non_blocking_fallback_evidence": True},
    }
    out = sec / "degraded_mode_evidence.json"
    write_json_report(out, report)
    print(f"DEGRADED_MODE_EVIDENCE: {report['status']}")
    print(f"Report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
