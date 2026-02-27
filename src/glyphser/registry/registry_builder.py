"""Operator registry builder from API-Interfaces.md (minimal)."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from src.glyphser.serialization.canonical_cbor import encode_canonical
import hashlib


def parse_api_interfaces(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    pattern = re.compile(r"\*\*Operator:\*\*\s+`([^`]+)`")
    return sorted({m.group(1) for m in pattern.finditer(text)})


def compute_signature_digest(
    operator_id: str,
    version: str,
    method: str,
    request_digest: bytes,
    response_digest: bytes,
    side_effects: list[str],
    allowed_error_codes: list[str],
) -> bytes:
    preimage = [
        "sig",
        operator_id,
        version,
        method,
        request_digest,
        response_digest,
        sorted(side_effects),
        sorted(allowed_error_codes),
    ]
    return hashlib.sha256(encode_canonical(preimage)).digest()


def build_operator_registry_from_list(
    operator_ids: list[str],
    digest_map: dict[str, bytes],
) -> dict[str, Any]:
    req = digest_map["schema.request.minimal"]
    resp = digest_map["schema.response.minimal"]

    records = []
    for operator_id in operator_ids:
        record = {
            "operator_id": operator_id,
            "version": "v1",
            "method": "CALL",
            "surface": "SYSCALL",
            "request_schema_digest": "sha256:schema.request.minimal",
            "response_schema_digest": "sha256:schema.response.minimal",
            "side_effects": ["READ_ONLY"],
            "allowed_error_codes": ["CONTRACT_VIOLATION"],
            "purity_class": "PURE",
        }
        record["signature_digest"] = compute_signature_digest(
            operator_id,
            record["version"],
            record["method"],
            req,
            resp,
            record["side_effects"],
            record["allowed_error_codes"],
        )
        records.append(record)

    return {
        "registry_schema_version": "v1",
        "operator_records": records,
    }
