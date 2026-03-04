#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from tooling.quality_gates.telemetry import emit_gate_trace

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SCHEMA = ROOT / "specs" / "schemas" / "evidence_metadata.schema.json"
LEGACY_DIR = ROOT / "artifacts" / "expected" / "schema_evolution"
OUT = ROOT / "evidence" / "gates" / "quality" / "schema_evolution.json"


MAPPING = {
    "id": "artifact_id",
    "artifact_path": "path",
    "digest_sha256": "sha256",
    "type": "evidence_type",
    "fixture": "source_fixture",
    "generator": "generated_by",
    "schema": "schema_version",
}


def _migrate_entry(legacy: dict) -> dict:
    out = dict(legacy)
    for old, new in MAPPING.items():
        if old in out and new not in out:
            out[new] = out.pop(old)
    return out


def evaluate() -> dict:
    findings: list[str] = []
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    required_entry = set(schema["properties"]["entries"]["items"]["required"])

    fixtures = sorted(LEGACY_DIR.glob("*.json")) if LEGACY_DIR.exists() else []
    if not fixtures:
        findings.append("no_legacy_schema_fixtures")

    migrated_count = 0
    for fixture in fixtures:
        data = json.loads(fixture.read_text(encoding="utf-8"))
        entries = data.get("entries", [])
        if not isinstance(entries, list):
            findings.append(f"invalid_entries_list:{fixture.name}")
            continue
        for idx, ent in enumerate(entries):
            if not isinstance(ent, dict):
                findings.append(f"invalid_entry_type:{fixture.name}:{idx}")
                continue
            migrated = _migrate_entry(ent)
            missing = sorted(required_entry - set(migrated.keys()))
            if missing:
                findings.append(f"missing_required_after_migration:{fixture.name}:{idx}:{','.join(missing)}")
            migrated_count += 1

    payload = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "legacy_fixture_count": len(fixtures),
        "migrated_entry_count": migrated_count,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    emit_gate_trace(ROOT, "schema_evolution", payload)
    return payload


def main() -> int:
    report = evaluate()
    if report["status"] == "PASS":
        print("SCHEMA_EVOLUTION_GATE: PASS")
        return 0
    print("SCHEMA_EVOLUTION_GATE: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
