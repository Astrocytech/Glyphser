"""Deterministic checkpoint restore (minimal)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from runtime.glyphser.security.path_guard import resolve_inside_root


_MAX_CHECKPOINT_BYTES = 10 * 1024 * 1024


def restore_checkpoint(request: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise ValueError("request must be dict")

    if "state" in request and isinstance(request["state"], dict):
        return {"state": request["state"]}

    path = request.get("path")
    if not path:
        raise ValueError("missing path")
    if not isinstance(path, str):
        raise ValueError("path must be string")
    if not path.endswith(".json"):
        raise ValueError("checkpoint path must end with .json")
    candidate = Path(path)
    if candidate.is_symlink():
        raise ValueError("symlink checkpoint paths are not allowed")
    allowed_root = request.get("allowed_root")
    if allowed_root:
        if not isinstance(allowed_root, str):
            raise ValueError("allowed_root must be string")
        candidate = resolve_inside_root(candidate, root=allowed_root, require_exists=True)
    if candidate.stat().st_size > _MAX_CHECKPOINT_BYTES:
        raise ValueError("checkpoint file too large")
    data = json.loads(candidate.read_text(encoding="utf-8"))
    return {"state": data}
