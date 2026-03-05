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

POLICY = ROOT / "governance" / "security" / "hardening_wip_limits_policy.json"
REGISTRY = ROOT / "governance" / "security" / "hardening_pending_item_registry.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    policy = _load_json(POLICY) if POLICY.exists() else {}
    registry = _load_json(REGISTRY) if REGISTRY.exists() else {}
    entries = registry.get("entries", []) if isinstance(registry.get("entries", []), list) else []
    limits = policy.get("wip_limits", {}) if isinstance(policy.get("wip_limits", {}), dict) else {}
    wave_map = policy.get("wave_section_prefixes", {}) if isinstance(policy.get("wave_section_prefixes", {}), dict) else {}
    counts: dict[str, int] = {str(k): 0 for k in limits.keys()}

    for row in entries:
        if not isinstance(row, dict):
            continue
        if str(row.get("status", "")).strip().lower() != "in_progress":
            continue
        section = str(row.get("section", "")).strip()
        for wave, prefixes_raw in wave_map.items():
            prefixes = [str(x).strip() for x in prefixes_raw if str(x).strip()] if isinstance(prefixes_raw, list) else []
            if any(section.startswith(prefix) for prefix in prefixes):
                counts[str(wave)] = counts.get(str(wave), 0) + 1

    for wave, limit in limits.items():
        try:
            max_wip = int(limit)
        except Exception:
            findings.append(f"invalid_wip_limit:{wave}")
            continue
        current = counts.get(str(wave), 0)
        if current > max_wip:
            findings.append(f"wip_limit_exceeded:{wave}:{current}:{max_wip}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"wip_counts": counts, "wip_limits": limits},
        "metadata": {"gate": "hardening_wip_limits_gate"},
    }
    out = evidence_root() / "security" / "hardening_wip_limits_gate.json"
    write_json_report(out, report)
    print(f"HARDENING_WIP_LIMITS_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
