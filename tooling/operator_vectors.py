#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
VECTORS_ROOT = ROOT / "artifacts" / "inputs" / "vectors" / "conformance" / "operators"


def operator_id_to_filename(operator_id: str) -> str:
    return operator_id.replace(".", "_") + ".json"


def load_vectors_file(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_vectors_payload(payload: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if not isinstance(payload, dict):
        return ["payload must be object"]

    operator_id = payload.get("operator_id")
    if not isinstance(operator_id, str) or not operator_id:
        errors.append("missing operator_id")

    vectors = payload.get("vectors")
    if not isinstance(vectors, list) or not vectors:
        errors.append("missing vectors")
        return errors

    for idx, vector in enumerate(vectors):
        if not isinstance(vector, dict):
            errors.append(f"vector[{idx}] must be object")
            continue
        if not isinstance(vector.get("case_id"), str) or not vector.get("case_id"):
            errors.append(f"vector[{idx}] missing case_id")
        if not isinstance(vector.get("request"), dict):
            errors.append(f"vector[{idx}] missing request")
        expected = vector.get("expected")
        if not isinstance(expected, dict):
            errors.append(f"vector[{idx}] missing expected")
        else:
            if "error" not in expected and "response" not in expected:
                errors.append(f"vector[{idx}] expected must include error or response")
            if "error" in expected:
                err = expected.get("error", {})
                if not isinstance(err, dict):
                    errors.append(f"vector[{idx}] error must be object")
                else:
                    for key in ("code_id", "message", "context"):
                        if key not in err:
                            errors.append(f"vector[{idx}] error missing {key}")
    return errors


def expected_vector_path(operator_id: str) -> Path:
    return VECTORS_ROOT / operator_id_to_filename(operator_id)


def enumerate_vector_files() -> List[Path]:
    if not VECTORS_ROOT.exists():
        return []
    return sorted(VECTORS_ROOT.glob("*.json"))


def ensure_root() -> None:
    VECTORS_ROOT.mkdir(parents=True, exist_ok=True)
