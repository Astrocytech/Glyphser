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


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    findings: list[str] = []
    events: list[dict[str, str]] = []

    for path in sorted(sec.glob("*.json")):
        if path.name == "incident_timeline_reconstruction.json":
            continue
        sig = path.with_suffix(path.suffix + ".sig")
        if not sig.exists():
            continue
        payload = _load_json(path)
        rel = str(path.relative_to(evidence_root())).replace("\\", "/")
        if payload is None:
            findings.append(f"invalid_signed_evidence_json:{rel}")
            continue
        metadata = payload.get("metadata", {}) if isinstance(payload, dict) else {}
        generated_at = str(metadata.get("generated_at_utc", "")).strip() if isinstance(metadata, dict) else ""
        if not generated_at:
            generated_at = "unknown"
        status = str(payload.get("status", "UNKNOWN")).upper()
        events.append(
            {
                "event_time_utc": generated_at,
                "artifact": rel,
                "status": status,
                "narrative": f"{path.stem} reported {status}.",
            }
        )

    events.sort(key=lambda item: (item.get("event_time_utc", ""), item.get("artifact", "")))
    if not events:
        findings.append("no_signed_security_evidence_for_timeline")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"timeline_events": len(events), "signed_artifacts": len(events)},
        "metadata": {"gate": "incident_timeline_reconstruction"},
        "timeline": events,
    }
    out = sec / "incident_timeline_reconstruction.json"
    write_json_report(out, report)
    print(f"INCIDENT_TIMELINE_RECONSTRUCTION: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
