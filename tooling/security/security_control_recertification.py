#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

MANIFEST = ROOT / "tooling" / "security" / "security_super_gate_manifest.json"


def _load_manifest() -> dict[str, Any]:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    now = datetime.now(UTC)
    findings: list[str] = []

    if not MANIFEST.exists():
        findings.append("missing_security_super_gate_manifest")
        manifest = {}
    else:
        try:
            manifest = _load_manifest()
        except Exception:
            manifest = {}
            findings.append("invalid_security_super_gate_manifest")

    core = [str(x) for x in manifest.get("core", []) if isinstance(x, str)] if isinstance(manifest, dict) else []
    extended = [str(x) for x in manifest.get("extended", []) if isinstance(x, str)] if isinstance(manifest, dict) else []

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "recertification_year": now.year,
            "recertified_at_utc": now.isoformat(),
            "core_controls": len(core),
            "extended_controls": len(extended),
            "total_controls": len(core) + len(extended),
        },
        "controls": {
            "core": sorted(core),
            "extended": sorted(extended),
        },
        "metadata": {
            "gate": "security_control_recertification",
            "owner": "security-governance",
            "next_recertification_due_utc": f"{now.year + 1}-12-31T23:59:59+00:00",
        },
    }

    out = evidence_root() / "security" / "security_control_recertification.json"
    write_json_report(out, report)
    sig = artifact_signing.sign_file(out, key=artifact_signing.current_key(strict=False))
    out.with_suffix(out.suffix + ".sig").write_text(sig + "\n", encoding="utf-8")
    print(f"SECURITY_CONTROL_RECERTIFICATION: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
