"""Minimal API signature validation helpers."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Iterable

from src.glyphser.registry.registry_builder import parse_api_interfaces


_DIGEST_RE = re.compile(r"^sha256:[a-z0-9._-]+$")


def validate_api_signature(record: Dict[str, Any], allowed_ops: Iterable[str] | None = None) -> None:
    if not isinstance(record, dict):
        raise TypeError("record must be a dict")

    for key in ("operator_id", "version", "method", "surface"):
        if key not in record or not isinstance(record[key], str) or not record[key]:
            raise ValueError(f"missing or invalid {key}")

    if allowed_ops is None:
        api_path = Path(__file__).resolve().parents[3] / "docs" / "layer1-foundation" / "API-Interfaces.md"
        allowed_ops = parse_api_interfaces(api_path)

    if record["operator_id"] not in set(allowed_ops):
        raise ValueError("operator_id not declared in API-Interfaces")

    for key in ("request_schema_digest", "response_schema_digest"):
        if key not in record or not isinstance(record[key], str) or not _DIGEST_RE.match(record[key]):
            raise ValueError(f"missing or invalid {key}")

    if "side_effects" in record and not isinstance(record["side_effects"], list):
        raise ValueError("side_effects must be a list")

    if "allowed_error_codes" in record and not isinstance(record["allowed_error_codes"], list):
        raise ValueError("allowed_error_codes must be a list")
