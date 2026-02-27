#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "contracts" / "operator_registry.json"
OUT = ROOT / "reports" / "coverage" / "operator_coverage.json"


def _load_registry_ops() -> List[str]:
    if not REGISTRY.exists():
        return []
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    return [r.get("operator_id", "") for r in data.get("operator_records", []) if r.get("operator_id")]


def _find_vector_files() -> Dict[str, List[str]]:
    mapping: Dict[str, List[str]] = {}
    vector_root = ROOT / "tests" / "conformance" / "vectors"
    if not vector_root.exists():
        return mapping

    for path in vector_root.rglob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        file_operator_id = data.get("operator_id")
        for vector in data.get("vectors", []):
            operator_id = vector.get("operator_id") or file_operator_id
            if not operator_id:
                continue
            rel = str(path.relative_to(ROOT)).replace("\\", "/")
            mapping.setdefault(operator_id, []).append(rel)

    return mapping


def _find_tests_for_ops(operators: List[str]) -> Dict[str, List[str]]:
    mapping: Dict[str, List[str]] = {op: [] for op in operators}
    test_root = ROOT / "tests"
    if not test_root.exists():
        return mapping

    for path in test_root.rglob("*.py"):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for op in operators:
            if op in text:
                rel = str(path.relative_to(ROOT)).replace("\\", "/")
                mapping[op].append(rel)
    return mapping


def generate() -> int:
    operators = sorted(_load_registry_ops())
    vector_map = _find_vector_files()
    test_map = _find_tests_for_ops(operators)

    coverage = []
    missing_vectors = []
    missing_tests = []

    for op in operators:
        vectors = sorted(set(vector_map.get(op, [])))
        tests = sorted(set(test_map.get(op, [])))
        coverage.append({"operator_id": op, "vectors": vectors, "tests": tests})
        if not vectors:
            missing_vectors.append(op)
        if not tests:
            missing_tests.append(op)

    summary = {
        "operator_count": len(operators),
        "missing_vectors": missing_vectors,
        "missing_tests": missing_tests,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps({"summary": summary, "coverage": coverage}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    if missing_vectors or missing_tests:
        print("COVERAGE: FAIL")
        print(f"missing_vectors={len(missing_vectors)} missing_tests={len(missing_tests)}")
        return 1

    print("COVERAGE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(generate())
