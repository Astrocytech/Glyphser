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

EXCEPTIONS_PATH = ROOT / "governance" / "security" / "temporary_exceptions.json"
CONTROL_MATRIX_PATH = ROOT / "governance" / "security" / "threat_control_matrix.json"


def _load_array(path: Path, field: str) -> list[dict[str, object]]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if not isinstance(payload, dict):
        return []
    raw = payload.get(field, [])
    if not isinstance(raw, list):
        return []
    out: list[dict[str, object]] = []
    for item in raw:
        if isinstance(item, dict):
            out.append(item)
    return out


def _active_control_ids(path: Path) -> set[str]:
    controls = _load_array(path, "controls")
    active: set[str] = set()
    for control in controls:
        control_id = str(control.get("id", "")).strip()
        if control_id:
            active.add(control_id)
    return active


def _exception_control_references(entry: dict[str, object]) -> set[str]:
    refs: set[str] = set()
    single = str(entry.get("control_id", "")).strip()
    if single:
        refs.add(single)
    multi = entry.get("control_ids", [])
    if isinstance(multi, list):
        for item in multi:
            value = str(item).strip()
            if value:
                refs.add(value)
    return refs


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    waivers_path = evidence_root() / "repro" / "waivers.json"
    exceptions = _load_array(EXCEPTIONS_PATH, "exceptions")
    waivers = _load_array(waivers_path, "waivers")
    active_control_ids = _active_control_ids(CONTROL_MATRIX_PATH)

    seen: dict[str, str] = {}
    duplicate_count = 0
    exceptions_with_control_refs = 0
    deleted_control_reference_count = 0

    for source, entries in (("exception", exceptions), ("waiver", waivers)):
        for idx, entry in enumerate(entries):
            value = str(entry.get("id", "")).strip()
            if not value:
                findings.append(f"missing_id:{source}:{idx}")
                continue
            key = value.casefold()
            if key in seen:
                duplicate_count += 1
                findings.append(f"duplicate_exception_waiver_id:{value}:{seen[key]}:{source}:{idx}")
            else:
                seen[key] = f"{source}:{idx}"

    if not active_control_ids:
        findings.append("missing_or_invalid_control_matrix")
    else:
        for idx, entry in enumerate(exceptions):
            refs = _exception_control_references(entry)
            if refs:
                exceptions_with_control_refs += 1
            for control_id in sorted(refs):
                if control_id not in active_control_ids:
                    deleted_control_reference_count += 1
                    findings.append(f"exception_references_deleted_control:{idx}:{control_id}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "exceptions_checked": len(exceptions),
            "waivers_checked": len(waivers),
            "duplicate_id_count": duplicate_count,
            "unique_ids_seen": len(seen),
            "active_control_ids": len(active_control_ids),
            "exceptions_with_control_refs": exceptions_with_control_refs,
            "deleted_control_reference_count": deleted_control_reference_count,
        },
        "metadata": {"gate": "exception_waiver_unique_id_gate"},
    }
    out = evidence_root() / "security" / "exception_waiver_unique_id_gate.json"
    write_json_report(out, report)
    print(f"EXCEPTION_WAIVER_UNIQUE_ID_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
