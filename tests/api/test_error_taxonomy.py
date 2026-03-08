from __future__ import annotations

from runtime.glyphser.api.error_taxonomy import classify_runtime_api_error


def test_runtime_api_error_taxonomy_is_deterministic() -> None:
    assert classify_runtime_api_error("missing auth token") == "AUTH_MISSING"
    assert classify_runtime_api_error("invalid scope: expected jobs:write") == "SCOPE_INVALID"
    assert classify_runtime_api_error("payload too deeply nested") == "PAYLOAD_TOO_DEEP"
    assert classify_runtime_api_error("token audience invalid") == "AUTH_TOKEN_AUDIENCE_INVALID"
    assert classify_runtime_api_error("unauthorized action: jobs:write") == "AUTH_UNAUTHORIZED_ACTION"


def test_runtime_api_error_taxonomy_falls_back_to_unknown() -> None:
    assert classify_runtime_api_error("totally novel runtime failure") == "UNKNOWN"
    assert classify_runtime_api_error("") == "UNKNOWN"
