"""Deterministic trace writer and hash helper (minimal)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable

from src.glyphser.trace.compute_trace_hash import compute_trace_hash


def write_trace(records: Iterable[Dict[str, Any]], path: Path) -> str:
    data = [r for r in records]
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    path.write_text(text + "\n", encoding="utf-8")
    return compute_trace_hash(data)
