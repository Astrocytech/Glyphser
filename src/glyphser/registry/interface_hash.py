"""Interface hash computation for operator registry."""
from __future__ import annotations

import hashlib
from typing import Any

from src.glyphser.serialization.canonical_cbor import encode_canonical


def compute_interface_hash(registry: dict[str, Any]) -> str:
    schema_version = registry.get("registry_schema_version")
    operator_records = registry.get("operator_records")
    preimage = ["operator_registry", schema_version, operator_records]
    digest = hashlib.sha256(encode_canonical(preimage)).hexdigest()
    return digest
