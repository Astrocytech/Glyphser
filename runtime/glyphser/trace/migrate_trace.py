"""Deterministic trace migration (minimal)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from runtime.glyphser.security.path_guard import resolve_inside_root, validate_path_text


def _validate_path_field(name: str, value: Any, *, allowed_root: str | None, require_exists: bool) -> None:
    if value is None:
        return
    normalized = validate_path_text(value, field_name=name)
    if not normalized.endswith(".json"):
        raise ValueError(f"{name} must end with .json")
    candidate = Path(normalized)
    if candidate.suffix == ".tmp":
        raise ValueError(f"{name} temporary file path is not allowed")
    if candidate.exists() and candidate.is_symlink():
        raise ValueError(f"{name} symlink path is not allowed")
    if allowed_root:
        _ = resolve_inside_root(candidate, root=allowed_root, require_exists=require_exists)
    elif candidate.is_absolute():
        raise ValueError(f"{name} absolute path requires allowed_root")


def migrate_trace(request: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise ValueError("request must be dict")
    allowed_root = request.get("allowed_root")
    if allowed_root is not None and not isinstance(allowed_root, str):
        raise ValueError("allowed_root must be string")
    _validate_path_field("trace_path", request.get("trace_path"), allowed_root=allowed_root, require_exists=True)
    _validate_path_field("output_path", request.get("output_path"), allowed_root=allowed_root, require_exists=False)
    trace = request.get("trace", {})
    return {"status": "OK", "trace": trace}
