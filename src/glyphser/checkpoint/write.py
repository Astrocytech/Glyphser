"""Deterministic checkpoint writer (minimal)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict

from src.glyphser.serialization.canonical_cbor import encode_canonical


def save_checkpoint(state: Dict[str, Any], path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(state, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    path.write_text(text + "\n", encoding="utf-8")
    digest = hashlib.sha256(encode_canonical(["checkpoint", state])).hexdigest()
    return digest
