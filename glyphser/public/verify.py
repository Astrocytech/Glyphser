"""Public verification entry point for deterministic execution."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from runtime.glyphser.model.model_ir_executor import execute


@dataclass(frozen=True)
class VerificationResult:
    digest: str
    output: dict[str, Any]


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def verify(
    model: dict[str, Any],
    input_data: dict[str, Any] | None = None,
) -> VerificationResult:
    """Execute a model deterministically and return a verification digest.

    Args:
        model: Model IR DAG dictionary.
        input_data: Optional model inputs.
    """
    if not isinstance(model, dict):
        raise TypeError("model must be a dict containing an IR DAG")

    request = {
        "ir_dag": model,
        "input_data": input_data or {},
        "driver_id": "default",
        "mode": "forward",
    }
    output = execute(request)
    digest = hashlib.sha256(_canonical_json(output).encode("utf-8")).hexdigest()
    return VerificationResult(digest=digest, output=output)


__all__ = ["VerificationResult", "verify"]
