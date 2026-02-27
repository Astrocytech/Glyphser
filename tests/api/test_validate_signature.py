from __future__ import annotations

import pytest

from src.glyphser.api.validate_signature import validate_api_signature


def test_validate_api_signature_ok():
    validate_api_signature(
        {
            "operator_id": "Glyphser.Data.NextBatch",
            "version": "v2",
            "method": "CALL",
            "surface": "SYSCALL",
            "request_schema_digest": "sha256:schema.request.minimal",
            "response_schema_digest": "sha256:schema.response.minimal",
            "side_effects": ["ADVANCES_CURSOR"],
            "allowed_error_codes": ["CONTRACT_VIOLATION"],
        }
    )

    validate_api_signature(
        {
            "operator_id": "Glyphser.Data.NextBatch",
            "version": "v2",
            "method": "CALL",
            "surface": "SYSCALL",
            "request_schema_digest": "sha256:schema.request.minimal",
            "response_schema_digest": "sha256:schema.response.minimal",
        },
        allowed_ops=["Glyphser.Data.NextBatch"],
    )


def test_validate_api_signature_rejects_missing():
    with pytest.raises(ValueError):
        validate_api_signature({"operator_id": "x"})


def test_validate_api_signature_rejects_unknown_operator():
    with pytest.raises(ValueError):
        validate_api_signature(
            {
                "operator_id": "Glyphser.Unknown.Op",
                "version": "v1",
                "method": "CALL",
                "surface": "SYSCALL",
                "request_schema_digest": "sha256:schema.request.minimal",
                "response_schema_digest": "sha256:schema.response.minimal",
            }
        )


def test_validate_api_signature_rejects_unknown_operator():
    with pytest.raises(ValueError):
        validate_api_signature(
            {
                "operator_id": "Glyphser.Unknown.Op",
                "version": "v1",
                "method": "CALL",
                "surface": "SYSCALL",
                "request_schema_digest": "sha256:schema.request.minimal",
                "response_schema_digest": "sha256:schema.response.minimal",
            }
        )
