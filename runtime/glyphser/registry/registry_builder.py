"""Operator registry builder from API-Interfaces.md."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from runtime.glyphser.serialization.canonical_cbor import encode_canonical


def _strip_ticks(value: str) -> str:
    value = value.strip()
    if value.startswith("`") and value.endswith("`"):
        return value[1:-1]
    return value


def _parse_json_array(value: str) -> list[str]:
    value = _strip_ticks(value)
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return []


def parse_api_interfaces(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        if "SYSCALL" not in line and "SERVICE" not in line:
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 10:
            continue
        surface = _strip_ticks(parts[0])
        operator_id = _strip_ticks(parts[1])
        version = _strip_ticks(parts[2])
        _kind = _strip_ticks(parts[3])
        request_schema_digest = _strip_ticks(parts[4])
        response_schema_digest = _strip_ticks(parts[5])
        pure = _strip_ticks(parts[6]).lower() == "true"
        side_effects = _parse_json_array(parts[7])
        allowed_error_codes = _parse_json_array(parts[8])
        signature_digest = _strip_ticks(parts[9])

        if side_effects == ["NONE"]:
            side_effects = []

        rng_usage = "PHILOX4x32_10" if "ADVANCES_RNG" in side_effects else "NONE"
        if pure:
            purity_class = "PURE"
        elif any(x in side_effects for x in ["PERFORMS_IO", "NETWORK_COMM"]):
            purity_class = "IO"
        else:
            purity_class = "STATEFUL"

        determinism_class = "STOCHASTIC" if rng_usage != "NONE" else "DETERMINISTIC"

        rows.append(
            {
                "operator_id": operator_id,
                "version": version,
                "method": "CALL",
                "surface": surface,
                "request_schema_digest": request_schema_digest,
                "response_schema_digest": response_schema_digest,
                "side_effects": side_effects,
                "allowed_error_codes": allowed_error_codes,
                "purity_class": purity_class,
                "rng_usage": rng_usage,
                "determinism_class": determinism_class,
                "required_capabilities": [],
                "signature_digest": signature_digest,
            }
        )
    return rows


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
    operator_records: list[dict[str, Any]],
    digest_map: dict[str, bytes],
) -> dict[str, Any]:
    req = digest_map["schema.request.minimal"]
    resp = digest_map["schema.response.minimal"]

    records = []
    for record in operator_records:
        record = dict(record)
        if not record.get("signature_digest"):
            record["signature_digest"] = compute_signature_digest(
                record["operator_id"],
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
