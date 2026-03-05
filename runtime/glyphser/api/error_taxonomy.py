"""Deterministic runtime API error code mapping."""

from __future__ import annotations

from typing import Final

_PREFIX_CODES: Final[list[tuple[str, str]]] = [
    ("missing auth token", "AUTH_MISSING"),
    ("token too long", "AUTH_TOKEN_TOO_LONG"),
    ("token too short", "AUTH_TOKEN_TOO_SHORT"),
    ("token format invalid", "AUTH_TOKEN_FORMAT_INVALID"),
    ("token entropy below minimum", "AUTH_TOKEN_LOW_ENTROPY"),
    ("token signature", "AUTH_TOKEN_SIGNATURE_INVALID"),
    ("token issuer invalid", "AUTH_TOKEN_ISSUER_INVALID"),
    ("token audience invalid", "AUTH_TOKEN_AUDIENCE_INVALID"),
    ("token expired", "AUTH_TOKEN_EXPIRED"),
    ("token scope mismatch", "AUTH_TOKEN_SCOPE_MISMATCH"),
    ("token jti", "AUTH_TOKEN_REPLAY"),
    ("signed token required", "AUTH_SIGNED_TOKEN_REQUIRED"),
    ("missing signed token verification key", "AUTH_SIGNING_KEY_MISSING"),
    ("unauthorized action", "AUTH_UNAUTHORIZED_ACTION"),
    ("invalid scope", "SCOPE_INVALID"),
    ("invalid job_id", "JOB_ID_INVALID"),
    ("payload too large", "PAYLOAD_TOO_LARGE"),
    ("payload too deeply nested", "PAYLOAD_TOO_DEEP"),
    ("payload too complex", "PAYLOAD_TOO_COMPLEX"),
    ("payload key not allowed", "PAYLOAD_KEY_INVALID"),
    ("submit payload contains unknown keys", "SUBMIT_UNKNOWN_FIELDS"),
    ("submit payload requires object field 'payload'", "SUBMIT_PAYLOAD_REQUIRED"),
    ("idempotency_key", "IDEMPOTENCY_KEY_INVALID"),
    ("quota exceeded", "QUOTA_EXCEEDED"),
    ("burst exceeded", "RATE_LIMIT_EXCEEDED"),
    ("cooldown", "COOLDOWN_ACTIVE"),
    ("missing job", "JOB_NOT_FOUND"),
    ("operation disabled by emergency lockdown policy", "LOCKDOWN_BLOCKED"),
]


def classify_runtime_api_error(message: str) -> str:
    text = (message or "").strip().lower()
    if not text:
        return "UNKNOWN"
    for prefix, code in _PREFIX_CODES:
        if prefix in text:
            return code
    return "UNKNOWN"
