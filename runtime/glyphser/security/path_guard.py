"""Filesystem safety guards for path-based runtime operations."""

from __future__ import annotations

from pathlib import Path


def resolve_inside_root(path: str | Path, *, root: str | Path, require_exists: bool = True) -> Path:
    root_path = Path(root).resolve()
    candidate = Path(path)
    resolved = candidate.resolve(strict=require_exists)
    if resolved.is_symlink():
        raise ValueError("symlink paths are not allowed")
    if resolved != root_path and root_path not in resolved.parents:
        raise ValueError("path escapes allowed root")
    return resolved
