"""Filesystem safety guards for path-based runtime operations."""

from __future__ import annotations

import unicodedata
from pathlib import Path

_CONFUSABLE_SEPARATORS = {"\u2215", "\u2044", "\uff0f", "\u29f8", "\u2216", "\uff3c"}
_CONFUSABLE_DOTS = {"\uff0e", "\u3002", "\uff61", "\u2024", "\ufe52"}


def validate_path_text(path_text: str, *, field_name: str) -> str:
    if not isinstance(path_text, str):
        raise ValueError(f"{field_name} must be string")
    if "\x00" in path_text:
        raise ValueError(f"{field_name} contains NUL")
    if any(ch in path_text for ch in _CONFUSABLE_SEPARATORS):
        raise ValueError(f"{field_name} contains unicode confusable separator")
    if any(ch in path_text for ch in _CONFUSABLE_DOTS):
        raise ValueError(f"{field_name} contains unicode confusable dot")
    if "/" in path_text and "\\" in path_text:
        raise ValueError(f"{field_name} contains mixed separators")

    normalized = unicodedata.normalize("NFKC", path_text)
    if ".." in normalized.replace("\\", "/").split("/"):
        raise ValueError(f"{field_name} contains traversal")
    return normalized


def resolve_inside_root(path: str | Path, *, root: str | Path, require_exists: bool = True) -> Path:
    root_path = Path(root).resolve()
    candidate = Path(path)
    resolved = candidate.resolve(strict=require_exists)
    if resolved.is_symlink():
        raise ValueError("symlink paths are not allowed")
    if resolved != root_path and root_path not in resolved.parents:
        raise ValueError("path escapes allowed root")
    return resolved
