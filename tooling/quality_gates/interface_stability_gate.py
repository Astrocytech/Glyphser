#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.quality_gates.telemetry import emit_gate_trace

SLA = ROOT / "specs" / "contracts" / "interface_stability_sla.json"
OUT = ROOT / "evidence" / "gates" / "quality" / "interface_stability.json"


def evaluate() -> dict:
    findings: list[str] = []
    if not SLA.exists():
        findings.append("missing_sla_file")
        payload = {"status": "FAIL", "findings": findings}
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        emit_gate_trace(ROOT, "interface_stability", payload)
        return payload

    data = json.loads(SLA.read_text(encoding="utf-8"))
    surf = data.get("public_surface", {})
    required_top = {"module", "stable_exports", "deprecation_window_minor_releases", "breaking_changes_require_major"}
    missing_top = sorted(required_top - set(surf.keys()))
    if missing_top:
        findings.append("missing_public_surface_keys:" + ",".join(missing_top))

    mod = importlib.import_module(surf.get("module", "glyphser"))
    exports = set(getattr(mod, "__all__", []))
    required_exports = set(surf.get("stable_exports", []))
    missing_exports = sorted(required_exports - exports)
    if missing_exports:
        findings.append("missing_stable_exports:" + ",".join(missing_exports))

    aliases = data.get("deprecated_aliases", [])
    for alias in aliases:
        symbol = alias.get("symbol", "")
        replacement = alias.get("replacement", "")
        if not symbol or not replacement:
            findings.append("invalid_deprecated_alias_entry")
            continue
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            present = hasattr(mod, symbol)
        if not present:
            findings.append(f"missing_deprecated_alias:{symbol}")
        if replacement not in exports:
            findings.append(f"missing_replacement_export:{replacement}")

    payload = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "stable_export_count": len(required_exports),
        "deprecated_alias_count": len(aliases),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    emit_gate_trace(ROOT, "interface_stability", payload)
    return payload


def main() -> int:
    report = evaluate()
    if report["status"] == "PASS":
        print("INTERFACE_STABILITY_GATE: PASS")
        return 0
    print("INTERFACE_STABILITY_GATE: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
