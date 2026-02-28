#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import List

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tooling.operator_vectors import (  # noqa: E402
    ensure_root,
    expected_vector_path,
    load_vectors_file,
    validate_vectors_payload,
)
REGISTRY = ROOT / "specs" / "contracts" / "operator_registry.json"


def _load_registry_ops() -> List[str]:
    if not REGISTRY.exists():
        return []
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    return [r.get("operator_id", "") for r in data.get("operator_records", []) if r.get("operator_id")]


def main() -> int:
    ensure_root()
    operators = _load_registry_ops()
    missing_files: List[str] = []
    invalid_files: List[str] = []

    for operator_id in operators:
        path = expected_vector_path(operator_id)
        if not path.exists():
            missing_files.append(str(path.relative_to(ROOT)).replace("\\", "/"))
            continue
        payload = load_vectors_file(path)
        errors = validate_vectors_payload(payload)
        if errors:
            invalid_files.append(f"{path}: {errors}")

    if missing_files or invalid_files:
        print("VECTOR_GATE: FAIL")
        if missing_files:
            print("missing vector files:")
            for p in missing_files:
                print(f" - {p}")
        if invalid_files:
            print("invalid vector files:")
            for entry in invalid_files:
                print(f" - {entry}")
        return 1

    print("VECTOR_GATE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
