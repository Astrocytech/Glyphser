#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "specs" / "contracts" / "operator_registry.json"
ERRORS = ROOT / "specs" / "layers" / "L1-foundation" / "Error-Codes.md"
MAPPING = ROOT / "specs" / "layers" / "L4-implementation" / "Code-Generation-Mapping.md"

DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def _read_registry() -> List[Dict[str, object]]:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    return data.get("operator_records", [])


def _parse_error_codes() -> set[str]:
    codes = set()
    for line in ERRORS.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if not parts:
            continue
        code = parts[0].strip("`")
        if code and code[0].isupper():
            codes.add(code)
    return codes


def _parse_mapping_ids() -> set[str]:
    ids = set()
    for line in MAPPING.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.startswith("| `Glyphser."):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if parts:
            ids.add(parts[0].strip("`").strip())
    return ids


def _lint_registry(records: List[Dict[str, object]]) -> List[str]:
    errors: List[str] = []
    for rec in records:
        op_id = rec.get("operator_id", "")
        for key in ["request_schema_digest", "response_schema_digest", "signature_digest"]:
            val = rec.get(key)
            if not isinstance(val, str) or not DIGEST_RE.match(val):
                errors.append(f"{op_id}: invalid digest {key}={val}")
        for key in ["side_effects", "allowed_error_codes", "required_capabilities"]:
            val = rec.get(key)
            if not isinstance(val, list):
                errors.append(f"{op_id}: missing or invalid {key}")
        if not isinstance(rec.get("method"), str):
            errors.append(f"{op_id}: missing method")
        if not isinstance(rec.get("version"), str):
            errors.append(f"{op_id}: missing version")
    return errors


def _lint_error_codes(records: List[Dict[str, object]], known: set[str]) -> List[str]:
    errors: List[str] = []
    for rec in records:
        op_id = rec.get("operator_id", "")
        codes = rec.get("allowed_error_codes", [])
        if not isinstance(codes, list):
            continue
        for code in codes:
            if code and code not in known:
                errors.append(f"{op_id}: unknown error code {code}")
    return errors


def _lint_mapping(records: List[Dict[str, object]], mapping_ids: set[str]) -> List[str]:
    errors: List[str] = []
    for rec in records:
        op_id = rec.get("operator_id", "")
        if op_id not in mapping_ids:
            errors.append(f"{op_id}: missing from Code-Generation-Mapping.md")
    return errors


def main() -> int:
    records = _read_registry()
    errors: List[str] = []
    errors.extend(_lint_registry(records))
    errors.extend(_lint_error_codes(records, _parse_error_codes()))
    errors.extend(_lint_mapping(records, _parse_mapping_ids()))

    if errors:
        print("SPEC_LINT: FAIL")
        for err in errors:
            print(f" - {err}")
        return 1

    print("SPEC_LINT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
