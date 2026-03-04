"""Deterministic checkpoint restore (minimal)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def restore_checkpoint(request: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise ValueError("request must be dict")

    if "state" in request and isinstance(request["state"], dict):
        return {"state": request["state"]}

    path = request.get("path")
    if not path:
        raise ValueError("missing path")

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {"state": data}
