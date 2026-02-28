"""Deterministic error emission helper (stub)."""
from __future__ import annotations

from typing import Any


def emit_error(code_id: str, message: str, **context: Any) -> dict[str, Any]:
    ordered_context = {k: context[k] for k in sorted(context.keys())}
    return {
        "code_id": code_id,
        "message": message,
        "context": ordered_context,
    }
