"""Deterministic trace migration (minimal)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def _validate_path_field(name: str, value: Any) -> None:
    if value is None:
        return
    if not isinstance(value, str):
        raise ValueError(f"{name} must be string")
    if "\x00" in value:
        raise ValueError(f"{name} contains NUL")
    if ".." in value.replace("\\", "/").split("/"):
        raise ValueError(f"{name} contains traversal")
    if not value.endswith(".json"):
        raise ValueError(f"{name} must end with .json")
    candidate = Path(value)
    if candidate.suffix == ".tmp":
        raise ValueError(f"{name} temporary file path is not allowed")
    if candidate.is_symlink():
        raise ValueError(f"{name} symlink path is not allowed")


def migrate_trace(request: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise ValueError("request must be dict")
    _validate_path_field("trace_path", request.get("trace_path"))
    _validate_path_field("output_path", request.get("output_path"))
    trace = request.get("trace", {})
    return {"status": "OK", "trace": trace}
