#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[2]
API = ROOT / "specs" / "layers" / "L1-foundation" / "API-Interfaces.md"
ERRORS = ROOT / "specs" / "layers" / "L1-foundation" / "Error-Codes.md"
VEC_ROOT = ROOT / "artifacts" / "inputs" / "vectors" / "primitives" / "operators"


def _parse_api() -> Dict[str, List[str]]:
    text = API.read_text(encoding="utf-8", errors="ignore")
    mapping: Dict[str, List[str]] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        if "SYSCALL" not in line and "SERVICE" not in line:
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 10:
            continue
        operator_id = parts[1].strip("`")
        allowed = parts[8].strip("`")
        try:
            codes = json.loads(allowed)
        except Exception:
            codes = []
        mapping[operator_id] = codes
    return mapping


def _parse_error_fields() -> Dict[str, List[str]]:
    text = ERRORS.read_text(encoding="utf-8", errors="ignore")
    mapping: Dict[str, List[str]] = {}
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 9:
            continue
        code_id = parts[0].strip("`")
        fields = parts[5].strip("`")
        if code_id and code_id[0].isupper():
            mapping[code_id] = [f for f in fields.split(",") if f]
    return mapping


def main() -> int:
    api_map = _parse_api()
    error_fields = _parse_error_fields()
    missing: List[str] = []
    incomplete: List[str] = []

    for operator_id, codes in api_map.items():
        vec_path = VEC_ROOT / (operator_id.replace(".", "_") + ".json")
        if not vec_path.exists():
            missing.append(operator_id)
            continue
        data = json.loads(vec_path.read_text(encoding="utf-8"))
        vectors = data.get("vectors", [])
        case_ids = {v.get("case_id") for v in vectors}
        for code in codes:
            if not code:
                continue
            base = f"{operator_id}.{code}.error"
            missing_field = f"{operator_id}.{code}.missing_field"
            type_mismatch = f"{operator_id}.{code}.type_mismatch"
            if base not in case_ids or missing_field not in case_ids or type_mismatch not in case_ids:
                incomplete.append(f"{operator_id}:{code}")

            # validate context fields
            required = error_fields.get(code, [])
            for v in vectors:
                if v.get("case_id") == base:
                    ctx = v.get("expected", {}).get("error", {}).get("context", {})
                    for field in required:
                        if field not in ctx:
                            incomplete.append(f"{operator_id}:{code}:missing_context:{field}")

    if missing or incomplete:
        print("ERROR_CODE_GATE: FAIL")
        for op in missing:
            print(f" - missing vectors for {op}")
        for item in incomplete:
            print(f" - incomplete: {item}")
        return 1

    print("ERROR_CODE_GATE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
