"""Deterministic execution certificate writer (minimal)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict

from src.glyphser.serialization.canonical_cbor import encode_canonical


def write_execution_certificate(evidence: Dict[str, Any], path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(evidence, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    path.write_text(text + "\n", encoding="utf-8")
    digest = hashlib.sha256(encode_canonical(["execution_certificate", evidence])).hexdigest()
    return digest
