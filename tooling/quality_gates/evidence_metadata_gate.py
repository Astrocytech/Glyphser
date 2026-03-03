#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "evidence" / "metadata" / "catalog.json"
SCHEMA = ROOT / "specs" / "schemas" / "evidence_metadata.schema.json"
OUT = ROOT / "evidence" / "gates" / "quality" / "evidence_metadata.json"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate() -> dict:
    findings: list[str] = []
    if not CATALOG.exists():
        findings.append("missing_catalog")
        payload = {"status": "FAIL", "findings": findings}
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return payload

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    required_top = set(schema.get("required", []))
    required_entry = set(schema["properties"]["entries"]["items"].get("required", []))

    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    missing_top = sorted(required_top - set(catalog.keys()))
    if missing_top:
        findings.append("missing_top_keys:" + ",".join(missing_top))

    entries = catalog.get("entries", [])
    if not isinstance(entries, list):
        findings.append("entries_not_list")
        entries = []

    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            findings.append(f"entry_{idx}_not_object")
            continue
        missing_entry = sorted(required_entry - set(entry.keys()))
        if missing_entry:
            findings.append(f"entry_{idx}_missing:" + ",".join(missing_entry))
            continue
        rel = entry["path"]
        target = ROOT / rel
        if not target.exists():
            findings.append(f"entry_{idx}_missing_file:{rel}")
            continue
        actual = _sha256(target)
        if entry["sha256"] != actual:
            findings.append(f"entry_{idx}_sha256_mismatch:{rel}")
        if not SHA256_RE.match(entry["sha256"]):
            findings.append(f"entry_{idx}_invalid_sha256:{rel}")

    payload = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "entry_count": len(entries),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    report = evaluate()
    if report["status"] == "PASS":
        print("EVIDENCE_METADATA_GATE: PASS")
        return 0
    print("EVIDENCE_METADATA_GATE: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
