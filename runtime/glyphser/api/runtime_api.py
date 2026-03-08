"""Versioned runtime API surface for Milestone 18."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import math
import os
import re
import threading
import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from runtime.glyphser.api.error_taxonomy import classify_runtime_api_error
from runtime.glyphser.security.audit import append_event
from runtime.glyphser.security.authz import authorize
from runtime.glyphser.security.zeroization import secret_bytes_buffer, zeroize_bytearray

try:
    import jsonschema
except Exception:  # pragma: no cover - fallback path for minimal environments
    jsonschema = None

_MAX_PAYLOAD_BYTES = 128 * 1024
_MAX_IDEMPOTENCY_KEY_LENGTH = 128
_MAX_SCOPE_LENGTH = 64
_MAX_TOKEN_LENGTH = 4096

_JOB_ID_RE = re.compile(r"^[0-9a-f]{24}$")
_PAYLOAD_KEY_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,64}$")
_IDEMPOTENCY_KEY_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_TOKEN_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,4096}$")


def _first_existing(candidates: list[Path]) -> Path:
    for path in candidates:
        if path.exists():
            return path
    return candidates[0]


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_payload(payload: Dict[str, Any], *, max_depth: int, max_items: int) -> None:
    if not isinstance(payload, dict):
        raise ValueError("payload must be dict")
    if len(payload) > 256:
        raise ValueError("payload has too many top-level keys")

    stack: list[tuple[Any, int]] = [(payload, 0)]
    seen_items = 0
    while stack:
        current, depth = stack.pop()
        seen_items += 1
        if seen_items > max_items:
            raise ValueError("payload too complex")
        if depth > max_depth:
            raise ValueError("payload too deeply nested")

        if isinstance(current, dict):
            for key, value in current.items():
                if not isinstance(key, str):
                    raise ValueError("payload keys must be strings")
                if not _PAYLOAD_KEY_RE.match(key):
                    raise ValueError(f"payload key not allowed: {key}")
                stack.append((value, depth + 1))
        elif isinstance(current, list):
            for value in current:
                stack.append((value, depth + 1))
        elif current is None or isinstance(current, (bool, int, float, str)):
            continue
        else:
            raise ValueError(f"unsupported payload type: {type(current).__name__}")


def _validate_submit_payload_schema(payload: Dict[str, Any]) -> None:
    allowed_keys = {"payload", "metadata", "tags"}
    unknown = sorted(k for k in payload if k not in allowed_keys)
    if unknown:
        raise ValueError(f"submit payload contains unknown keys: {', '.join(unknown)}")

    body = payload.get("payload")
    if not isinstance(body, dict):
        raise ValueError("submit payload requires object field 'payload'")

    metadata = payload.get("metadata")
    if metadata is not None:
        if not isinstance(metadata, dict):
            raise ValueError("submit metadata must be an object")
        if len(metadata) > 64:
            raise ValueError("submit metadata has too many keys")
        for key, value in metadata.items():
            if not isinstance(key, str) or not _PAYLOAD_KEY_RE.match(key):
                raise ValueError("submit metadata keys must be safe strings")
            if value is None or isinstance(value, (bool, int, float, str)):
                continue
            raise ValueError("submit metadata values must be scalar")

    tags = payload.get("tags")
    if tags is not None:
        if not isinstance(tags, list):
            raise ValueError("submit tags must be a list")
        if len(tags) > 32:
            raise ValueError("submit tags has too many entries")
        for tag in tags:
            if not isinstance(tag, str) or not tag or len(tag) > 32 or not _PAYLOAD_KEY_RE.match(tag):
                raise ValueError("submit tags must be safe short strings")


def _matches_schema_type(value: Any, schema_type: str) -> bool:
    if schema_type == "object":
        return isinstance(value, dict)
    if schema_type == "array":
        return isinstance(value, list)
    if schema_type == "string":
        return isinstance(value, str)
    if schema_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if schema_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if schema_type == "boolean":
        return isinstance(value, bool)
    if schema_type == "null":
        return value is None
    return True


@lru_cache(maxsize=1)
def _runtime_api_schemas() -> dict[str, Any]:
    schema_path = Path(__file__).resolve().parent / "schemas" / "runtime_api_schemas.json"
    payload = json.loads(schema_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("runtime api schemas must be an object")
    return payload


def _validate_against_schema(name: str, payload: dict[str, Any]) -> None:
    schemas = _runtime_api_schemas()
    schema = schemas.get(name)
    if not isinstance(schema, dict):
        raise ValueError(f"missing schema: {name}")
    if not isinstance(payload, dict):
        raise ValueError(f"{name}: payload must be object")
    if jsonschema is None:
        # Fallback validator keeps deterministic behavior when jsonschema is unavailable.
        if schema.get("type") != "object":
            raise ValueError(f"schema {name} must be object")
        required = schema.get("required", [])
        properties = schema.get("properties", {})
        additional = bool(schema.get("additionalProperties", True))
        if not isinstance(required, list) or not isinstance(properties, dict):
            raise ValueError(f"invalid schema layout: {name}")
        for key in required:
            if key not in payload:
                raise ValueError(f"{name}: missing required field {key}")
        for key, value in payload.items():
            prop = properties.get(key)
            if prop is None:
                if not additional:
                    raise ValueError(f"{name}: unknown field {key}")
                continue
            if not isinstance(prop, dict):
                raise ValueError(f"{name}: invalid field schema {key}")
            field_type = str(prop.get("type", "")).strip()
            if field_type and not _matches_schema_type(value, field_type):
                raise ValueError(f"{name}: invalid type for field {key}")
        return

    validator = jsonschema.Draft7Validator(schema)
    errors = sorted(
        validator.iter_errors(payload),
        key=lambda err: (list(err.path), list(err.schema_path), err.message),
    )
    if errors:
        first = errors[0]
        location = ".".join(str(x) for x in first.path)
        where = f" at {location}" if location else ""
        raise ValueError(f"{name}{where}: {first.message}")


def _validate_scope(scope: str, *, expected: str) -> None:
    if not isinstance(scope, str) or not scope:
        raise ValueError("missing scope")
    if len(scope) > _MAX_SCOPE_LENGTH:
        raise ValueError("scope too long")
    if scope != expected:
        raise ValueError(f"invalid scope: expected {expected}")


def _validate_job_id(job_id: str) -> None:
    if not isinstance(job_id, str) or not _JOB_ID_RE.match(job_id):
        raise ValueError("invalid job_id")


def _load_lockdown_policy(root: Path) -> dict[str, Any]:
    path = root / "governance" / "security" / "emergency_lockdown_policy.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _shannon_entropy_bits(text: str) -> float:
    if not text:
        return 0.0
    counts: dict[str, int] = {}
    for ch in text:
        counts[ch] = counts.get(ch, 0) + 1
    total = float(len(text))
    entropy = 0.0
    for count in counts.values():
        p = count / total
        if p > 0.0:
            entropy -= p * math.log2(p)
    return entropy * len(text)


def _b64url_decode(data: str) -> bytes:
    pad = "=" * ((4 - (len(data) % 4)) % 4)
    return base64.urlsafe_b64decode(data + pad)


@dataclass(frozen=True)
class RuntimeApiConfig:
    root: Path
    state_path: Path
    audit_log_path: Path | None = None
    api_version: str = "1.0.0"
    max_requests_per_token: int = 10_000
    max_submits_per_token: int = 2_000
    max_reads_per_job: int = 10_000
    max_replays_per_job: int = 2_000
    replay_cooldown_seconds: int = 1
    max_requests_per_window: int = 250
    request_window_seconds: int = 60
    max_replays_per_token_window: int = 30
    max_replays_per_job_window: int = 10
    replay_window_seconds: int = 60
    max_cross_token_replays_per_job_window: int = 5
    max_job_reads_per_window: int = 120
    job_read_window_seconds: int = 60
    auth_failure_denylist_threshold: int = 5
    auth_failure_denylist_cooldown_seconds: int = 300
    enforce_token_policy: bool = True
    min_token_entropy_bits: int = 24
    submit_request_max_bytes: int = 256 * 1024
    status_request_max_bytes: int = 2 * 1024
    evidence_request_max_bytes: int = 2 * 1024
    replay_request_max_bytes: int = 2 * 1024
    submit_payload_max_bytes: int = _MAX_PAYLOAD_BYTES
    submit_payload_max_depth: int = 16
    submit_payload_max_items: int = 50_000
    include_replay_failure_reason: bool = False
    enforce_replay_token_binding: bool = False
    replay_token_ttl_seconds: int = 86_400
    replay_token_max_uses: int = 500
    idempotency_ttl_seconds: int = 86_400
    idempotency_max_entries: int = 10_000
    enforce_signed_tokens: bool = False
    token_hmac_key_env: str = "GLYPHSER_RUNTIME_API_TOKEN_HMAC_KEY"
    token_issuer: str = "glyphser-runtime"
    token_audience: str = "glyphser-runtime-api"
    token_clock_skew_seconds: int = 60
    enforce_token_jti_replay_protection: bool = False
    token_jti_ttl_seconds: int = 3600
    token_jti_max_entries: int = 10_000


class RuntimeApiService:
    """Minimal deterministic API service with file-backed state."""

    def __init__(self, config: RuntimeApiConfig) -> None:
        self._config = config
        self._enforce_safe_runtime_defaults()
        self._lock = threading.RLock()
        self._config.state_path.parent.mkdir(parents=True, exist_ok=True)

    def _enforce_safe_runtime_defaults(self) -> None:
        env_hint = os.environ.get("GLYPHSER_ENV", "").strip().lower()
        if env_hint not in {"staging", "prod", "production", "release"}:
            return
        allow_risky = os.environ.get("GLYPHSER_ALLOW_RISKY_RUNTIME_DEFAULTS", "").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        if allow_risky:
            return
        risky: list[str] = []
        if not self._config.enforce_signed_tokens:
            risky.append("enforce_signed_tokens=False")
        if not self._config.enforce_token_jti_replay_protection:
            risky.append("enforce_token_jti_replay_protection=False")
        if not self._config.enforce_replay_token_binding:
            risky.append("enforce_replay_token_binding=False")
        if risky:
            joined = ", ".join(risky)
            raise ValueError(
                "unsafe runtime api defaults in production path; set explicit secure values "
                f"or GLYPHSER_ALLOW_RISKY_RUNTIME_DEFAULTS=1 (temporary): {joined}"
            )

    def submit_job(
        self,
        payload: Dict[str, Any],
        token: str,
        scope: str,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        _validate_against_schema(
            "submit_request",
            {
                "payload": payload,
                "token": token,
                "scope": scope,
                "idempotency_key": idempotency_key or "",
            },
        )
        self._enforce_request_size(
            {"payload": payload, "token": token, "scope": scope, "idempotency_key": idempotency_key or ""},
            limit=self._config.submit_request_max_bytes,
            error="submit request too large",
        )
        _validate_scope(scope, expected="jobs:write")
        self._enforce_lockdown("publish")
        self._require_auth_with_tracking(token=token, action="jobs:write", scope=scope, job_id="")
        _validate_payload(
            payload,
            max_depth=max(1, int(self._config.submit_payload_max_depth)),
            max_items=max(1, int(self._config.submit_payload_max_items)),
        )
        _validate_submit_payload_schema(payload)
        if idempotency_key and len(idempotency_key) > _MAX_IDEMPOTENCY_KEY_LENGTH:
            raise ValueError("idempotency_key too long")
        if idempotency_key and not _IDEMPOTENCY_KEY_RE.match(idempotency_key):
            raise ValueError("idempotency_key has invalid characters")
        with self._lock:
            state = self._load_state()
            self._prune_idempotency(state)
            payload_text = _canonical_json(payload)
            payload_hash = _sha256_text(payload_text)
            self._bump_token_quota(
                state,
                token=token,
                action="jobs:write",
                request_limit=self._effective_request_limit(token=token, action="jobs:write"),
                submit_limit=self._effective_submit_limit(token=token),
                window_limit=self._config.max_requests_per_window,
                window_seconds=self._config.request_window_seconds,
            )

            if idempotency_key:
                existing = self._idempotency_job(state, idempotency_key)
                if existing:
                    existing_record = state["jobs"].get(existing, {})
                    if isinstance(existing_record, dict):
                        existing_hash = str(existing_record.get("payload_hash", "")).strip()
                        if existing_hash and existing_hash != payload_hash:
                            collisions = state["quotas"].setdefault("idempotency_collisions", {})
                            if not isinstance(collisions, dict):
                                collisions = {}
                                state["quotas"]["idempotency_collisions"] = collisions
                            current = collisions.get(idempotency_key, 0)
                            if not isinstance(current, int) or current < 0:
                                current = 0
                            collisions[idempotency_key] = current + 1
                            provenance = state.setdefault("collision_provenance", {})
                            if not isinstance(provenance, dict):
                                provenance = {}
                                state["collision_provenance"] = provenance
                            provenance_key = f"{idempotency_key}:{int(time.time())}:{current + 1}"
                            provenance[provenance_key] = {
                                "idempotency_key": idempotency_key,
                                "existing_job_id": existing,
                                "existing_payload_hash": existing_hash,
                                "incoming_payload_hash": payload_hash,
                                "token_hash": _sha256_text(token),
                                "scope": scope,
                                "timestamp": int(time.time()),
                            }
                            self._save_state(state)
                    out = dict(state["jobs"][existing])
                    _validate_against_schema("submit_response", out)
                    self._audit("status", token=token, job_id=existing, scope=scope)
                    return out

            if len(payload_text.encode("utf-8")) > max(1, int(self._config.submit_payload_max_bytes)):
                raise ValueError("payload too large")
            basis = f"job:{idempotency_key or payload_text}"
            job_id = _sha256_text(basis)[:24]
            trace_id = _sha256_text(f"trace:{job_id}:{payload_text}")[:32]
            record = {
                "job_id": job_id,
                "trace_id": trace_id,
                "status": "accepted",
                "api_version": self._config.api_version,
                "payload_hash": payload_hash,
                "idempotency_key": idempotency_key or "",
            }
            state["jobs"][job_id] = record
            state["replay_tokens"][job_id] = {
                "minted_at": int(time.time()),
                "bound_token_hash": _sha256_text(token),
                "uses": 0,
                "revoked": False,
            }
            if idempotency_key:
                state["idempotency"][idempotency_key] = job_id
                state["idempotency_meta"][idempotency_key] = {"job_id": job_id, "ts": int(time.time())}
            self._save_state(state)
            self._audit("submit", token=token, job_id=job_id, scope=scope)
            _validate_against_schema("submit_response", record)
            return dict(record)

    def status(self, job_id: str, token: str, scope: str) -> Dict[str, Any]:
        _validate_against_schema("status_request", {"job_id": job_id, "token": token, "scope": scope})
        self._enforce_request_size(
            {"job_id": job_id, "token": token, "scope": scope},
            limit=self._config.status_request_max_bytes,
            error="status request too large",
        )
        _validate_scope(scope, expected="jobs:read")
        _validate_job_id(job_id)
        self._require_auth_with_tracking(token=token, action="jobs:read", scope=scope, job_id=job_id)
        with self._lock:
            state = self._load_state()
            self._bump_token_quota(
                state,
                token=token,
                action="jobs:read",
                request_limit=self._effective_request_limit(token=token, action="jobs:read"),
                window_limit=self._config.max_requests_per_window,
                window_seconds=self._config.request_window_seconds,
            )
            out = self._require_job_locked(state, job_id)
            self._bump_job_read_quota(state, job_id=job_id, limit=self._config.max_reads_per_job)
            self._bump_window_counter(
                state["quotas"]["job_read_window"],
                key=job_id,
                limit=self._config.max_job_reads_per_window,
                window_seconds=self._config.job_read_window_seconds,
                error="job read burst exceeded",
            )
            self._save_state(state)
            self._audit("status", token=token, job_id=job_id, scope=scope)
            _validate_against_schema("status_response", out)
            return out

    def evidence(self, job_id: str, token: str, scope: str) -> Dict[str, Any]:
        _validate_against_schema("evidence_request", {"job_id": job_id, "token": token, "scope": scope})
        self._enforce_request_size(
            {"job_id": job_id, "token": token, "scope": scope},
            limit=self._config.evidence_request_max_bytes,
            error="evidence request too large",
        )
        _validate_scope(scope, expected="evidence:read")
        _validate_job_id(job_id)
        self._require_auth_with_tracking(token=token, action="evidence:read", scope=scope, job_id=job_id)
        with self._lock:
            state = self._load_state()
            self._bump_token_quota(
                state,
                token=token,
                action="evidence:read",
                request_limit=self._effective_request_limit(token=token, action="evidence:read"),
                window_limit=self._config.max_requests_per_window,
                window_seconds=self._config.request_window_seconds,
            )
            _ = self._require_job_locked(state, job_id)
            self._bump_job_read_quota(state, job_id=job_id, limit=self._config.max_reads_per_job)
            self._bump_window_counter(
                state["quotas"]["job_read_window"],
                key=job_id,
                limit=self._config.max_job_reads_per_window,
                window_seconds=self._config.job_read_window_seconds,
                error="job read burst exceeded",
            )
            self._save_state(state)
            root = self._config.root
            conformance = root / "conformance" / "reports" / "latest.json"
            bundle_manifest = _first_existing(
                [
                    root / "artifacts" / "bundles" / "hello-core-bundle.sha256",
                    root / "dist" / "hello-core-bundle.sha256",
                ]
            )
            repro = _first_existing(
                [
                    root / "evidence" / "repro" / "hashes.txt",
                    root / "reports" / "repro" / "hashes.txt",
                ]
            )
            out = {
                "job_id": job_id,
                "api_version": self._config.api_version,
                "conformance_report_hash": _sha256_file(conformance) if conformance.exists() else "",
                "bundle_manifest_line": bundle_manifest.read_text(encoding="utf-8").strip()
                if bundle_manifest.exists()
                else "",
                "repro_hash_line": repro.read_text(encoding="utf-8").strip() if repro.exists() else "",
            }
            self._audit("evidence", token=token, job_id=job_id, scope=scope)
            _validate_against_schema("evidence_response", out)
            return out

    def replay(self, job_id: str, token: str, scope: str) -> Dict[str, Any]:
        _validate_against_schema("replay_request", {"job_id": job_id, "token": token, "scope": scope})
        self._enforce_request_size(
            {"job_id": job_id, "token": token, "scope": scope},
            limit=self._config.replay_request_max_bytes,
            error="replay request too large",
        )
        _validate_scope(scope, expected="replay:run")
        self._enforce_lockdown("replay")
        _validate_job_id(job_id)
        self._require_auth_with_tracking(token=token, action="replay:run", scope=scope, job_id=job_id)
        with self._lock:
            state = self._load_state()
            self._bump_token_quota(
                state,
                token=token,
                action="replay:run",
                request_limit=self._effective_request_limit(token=token, action="replay:run"),
                window_limit=self._config.max_requests_per_window,
                window_seconds=self._config.request_window_seconds,
            )
            _ = self._require_job_locked(state, job_id)
            self._bump_job_read_quota(state, job_id=job_id, limit=self._config.max_reads_per_job)
            self._bump_window_counter(
                state["quotas"]["job_read_window"],
                key=job_id,
                limit=self._config.max_job_reads_per_window,
                window_seconds=self._config.job_read_window_seconds,
                error="job read burst exceeded",
            )
            self._enforce_replay_token_lifecycle(state=state, job_id=job_id, token=token)
            self._enforce_replay_cooldown(state, job_id=job_id, cooldown_seconds=self._config.replay_cooldown_seconds)
            self._bump_job_replay_quota(state, job_id=job_id, limit=self._config.max_replays_per_job)
            self._bump_replay_window_quota(
                state,
                token=token,
                job_id=job_id,
                token_limit=self._effective_replay_token_window_limit(token=token),
                job_limit=self._config.max_replays_per_job_window,
                cross_token_limit=self._config.max_cross_token_replays_per_job_window,
                window_seconds=self._config.replay_window_seconds,
            )
            self._save_state(state)
            ev = self._build_evidence(job_id)
            bundle_line = ev["bundle_manifest_line"]
            repro_line = ev["repro_hash_line"]
            if not bundle_line or not repro_line:
                out = {
                    "job_id": job_id,
                    "api_version": self._config.api_version,
                    "replay_verdict": "FAIL",
                }
                if self._config.include_replay_failure_reason:
                    out["reason"] = "missing evidence"
                self._audit(
                    "replay",
                    token=token,
                    job_id=job_id,
                    scope=scope,
                    replay_verdict="FAIL",
                )
                _validate_against_schema("replay_response", out)
                return out
            verdict = "PASS" if bundle_line == repro_line else "FAIL"
            out = {
                "job_id": job_id,
                "api_version": self._config.api_version,
                "replay_verdict": verdict,
            }
            self._audit(
                "replay",
                token=token,
                job_id=job_id,
                scope=scope,
                replay_verdict=verdict,
            )
            _validate_against_schema("replay_response", out)
            return out

    @staticmethod
    def _roles_from_token(token: str, claims: dict[str, Any] | None = None) -> list[str]:
        if isinstance(claims, dict):
            raw_roles = claims.get("roles", [])
            if isinstance(raw_roles, list):
                roles = [str(x).strip() for x in raw_roles if isinstance(x, str) and str(x).strip()]
                if roles:
                    return roles
        if token.startswith("role:"):
            return [token.split(":", 1)[1]]
        return ["admin"]

    def _token_hmac_key(self) -> str:
        return os.environ.get(self._config.token_hmac_key_env, "")

    def _parse_signed_token_claims(self, token: str) -> dict[str, Any] | None:
        if not token.startswith("sig:"):
            return None
        raw = token[4:]
        if "." not in raw:
            raise ValueError("token signature format invalid")
        payload_b64, sig_hex = raw.rsplit(".", 1)
        if not payload_b64 or not sig_hex:
            raise ValueError("token signature format invalid")
        key = self._token_hmac_key()
        if not key:
            raise ValueError("missing signed token verification key")
        with secret_bytes_buffer(key) as key_buf, secret_bytes_buffer(payload_b64, encoding="ascii") as payload_buf:
            expected = hmac.new(bytes(key_buf), bytes(payload_buf), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, sig_hex):
            raise ValueError("token signature invalid")
        claims_bytes = bytearray()
        try:
            claims_bytes = bytearray(_b64url_decode(payload_b64))
            claims_raw = claims_bytes.decode("utf-8")
            claims = json.loads(claims_raw)
        except Exception as exc:
            raise ValueError("token payload invalid") from exc
        finally:
            zeroize_bytearray(claims_bytes)
        if not isinstance(claims, dict):
            raise ValueError("token claims invalid")
        return claims

    def _validate_signed_token(self, token: str, *, scope: str, state: dict[str, Any] | None = None) -> dict[str, Any]:
        claims = self._parse_signed_token_claims(token)
        if claims is None:
            if self._config.enforce_signed_tokens:
                raise ValueError("signed token required")
            return {}
        iss = str(claims.get("iss", "")).strip()
        aud = str(claims.get("aud", "")).strip()
        if iss != self._config.token_issuer:
            raise ValueError("token issuer invalid")
        valid_aud = {self._config.token_audience, f"{self._config.token_audience}:{scope}", scope}
        if aud not in valid_aud:
            raise ValueError("token audience invalid")
        exp = claims.get("exp")
        now = int(time.time())
        skew = max(0, int(self._config.token_clock_skew_seconds))
        if not isinstance(exp, int):
            raise ValueError("token expiry invalid")
        if exp < (now - skew):
            raise ValueError("token expired")
        token_scope = str(claims.get("scope", "")).strip()
        if token_scope and token_scope != scope:
            raise ValueError("token scope mismatch")
        if self._config.enforce_token_jti_replay_protection:
            jti = str(claims.get("jti", "")).strip()
            if not jti:
                raise ValueError("token jti missing")
            if state is None:
                raise ValueError("token state required")
            self._prune_token_jti_cache(state)
            seen = state.setdefault("token_jti_seen", {})
            if not isinstance(seen, dict):
                raise ValueError("invalid token_jti_seen state")
            if jti in seen:
                raise ValueError("token jti replay detected")
            seen[jti] = now
        return claims

    def _token_policy_enforced(self) -> bool:
        if not self._config.enforce_token_policy:
            return False
        env_hint = os.environ.get("GLYPHSER_ENV", "").strip().lower()
        return env_hint not in {"", "local", "dev", "test"}

    def _enforce_lockdown(self, operation: str) -> None:
        policy = _load_lockdown_policy(self._config.root)
        if not policy:
            return
        if policy.get("lockdown_enabled") is not True:
            return
        if operation == "publish" and policy.get("disable_publish") is True:
            raise ValueError("operation disabled by emergency lockdown policy")
        if operation == "replay" and policy.get("disable_replay") is True:
            raise ValueError("operation disabled by emergency lockdown policy")

    def _effective_request_limit(self, *, token: str, action: str) -> int:
        roles = self._roles_from_token(token)
        role = roles[0] if roles else "admin"
        base = self._config.max_requests_per_token
        if role in {"viewer", "reader"}:
            return min(base, max(10, base // 4))
        if action == "replay:run":
            return min(base, max(10, base // 2))
        return base

    def _effective_submit_limit(self, *, token: str) -> int:
        roles = self._roles_from_token(token)
        role = roles[0] if roles else "admin"
        base = self._config.max_submits_per_token
        if role in {"viewer", "reader"}:
            return min(base, max(5, base // 10))
        return base

    def _effective_replay_token_window_limit(self, *, token: str) -> int:
        roles = self._roles_from_token(token)
        role = roles[0] if roles else "admin"
        base = self._config.max_replays_per_token_window
        if role in {"viewer", "reader"}:
            return min(base, max(1, base // 3))
        return base

    def _require_auth(self, token: str, action: str, *, scope: str, state: dict[str, Any] | None = None) -> None:
        if not isinstance(token, str) or not token.strip():
            raise ValueError("missing auth token")
        if len(token) > _MAX_TOKEN_LENGTH:
            raise ValueError("token too long")
        claims = self._validate_signed_token(token, scope=scope, state=state)
        if self._token_policy_enforced():
            if len(token) < 8 and not token.startswith("role:"):
                raise ValueError("token too short")
            if not _TOKEN_RE.match(token):
                raise ValueError("token format invalid")
            if token.startswith("token-") or token.endswith("-token") or token in {"token-a", "token-b"}:
                raise ValueError("weak token pattern not allowed")
            if _shannon_entropy_bits(token) < float(self._config.min_token_entropy_bits):
                raise ValueError("token entropy below minimum")
        roles = self._roles_from_token(token, claims=claims)
        if not authorize(action, roles):
            raise ValueError(f"unauthorized action: {action}")

    def _require_auth_with_tracking(self, *, token: str, action: str, scope: str, job_id: str) -> None:
        try:
            with self._lock:
                state = self._load_state()
                self._enforce_auth_failure_cooldown(state, token=token)
                self._require_auth(token=token, action=action, scope=scope, state=state)
                self._save_state(state)
        except ValueError as exc:
            with self._lock:
                state = self._load_state()
                self._record_auth_failure(state, token=token)
                self._save_state(state)
            self._audit(
                "auth_failure",
                token=token,
                job_id=job_id,
                scope=scope,
                auth_error_code=classify_runtime_api_error(str(exc)),
            )
            raise

    def _audit(
        self,
        operation: str,
        token: str,
        job_id: str,
        scope: str,
        replay_verdict: str = "",
        auth_error_code: str = "",
    ) -> None:
        path = self._config.audit_log_path or self._config.state_path.parent / "audit.log.jsonl"
        append_event(
            path,
            {
                "operation": operation,
                "job_id": job_id,
                "scope": scope,
                # Never persist raw auth tokens in audit artifacts.
                "role_token_hash": _sha256_text(token),
                "role_token_kind": "role" if token.startswith("role:") else "token",
                "replay_verdict": replay_verdict,
                "auth_error_code": auth_error_code,
            },
        )

    def _load_state(self) -> Dict[str, Any]:
        if not self._config.state_path.exists():
            return {
                "jobs": {},
                "idempotency": {},
                "idempotency_meta": {},
                "collision_provenance": {},
                "replay_tokens": {},
                "token_jti_seen": {},
                "quotas": {
                    "token_requests": {},
                    "token_submits": {},
                    "job_reads": {},
                    "job_replays": {},
                    "job_last_replay_ts": {},
                    "token_request_window": {},
                    "auth_failures_by_token": {},
                    "auth_failure_cooldown_until": {},
                    "replay_window_by_token": {},
                    "replay_window_by_job": {},
                    "replay_window_job_tokens": {},
                    "idempotency_collisions": {},
                    "job_read_window": {},
                },
            }
        data = json.loads(self._config.state_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("invalid state")
        data.setdefault("jobs", {})
        data.setdefault("idempotency", {})
        data.setdefault("idempotency_meta", {})
        data.setdefault("collision_provenance", {})
        data.setdefault("replay_tokens", {})
        data.setdefault("token_jti_seen", {})
        quotas = data.setdefault("quotas", {})
        if not isinstance(quotas, dict):
            raise ValueError("invalid state quotas")
        quotas.setdefault("token_requests", {})
        quotas.setdefault("token_submits", {})
        quotas.setdefault("job_reads", {})
        quotas.setdefault("job_replays", {})
        quotas.setdefault("job_last_replay_ts", {})
        quotas.setdefault("token_request_window", {})
        quotas.setdefault("auth_failures_by_token", {})
        quotas.setdefault("auth_failure_cooldown_until", {})
        quotas.setdefault("replay_window_by_token", {})
        quotas.setdefault("replay_window_by_job", {})
        quotas.setdefault("replay_window_job_tokens", {})
        quotas.setdefault("idempotency_collisions", {})
        quotas.setdefault("job_read_window", {})
        if not isinstance(data.get("token_jti_seen"), dict):
            raise ValueError("invalid token_jti_seen")
        return data

    def _save_state(self, state: Dict[str, Any]) -> None:
        self._config.state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def _prune_idempotency(self, state: Dict[str, Any]) -> None:
        ttl = max(1, int(self._config.idempotency_ttl_seconds))
        cap = max(1, int(self._config.idempotency_max_entries))
        now = int(time.time())
        idx = state.get("idempotency_meta", {})
        if not isinstance(idx, dict):
            idx = {}
            state["idempotency_meta"] = idx
        legacy = state.get("idempotency", {})
        if not isinstance(legacy, dict):
            legacy = {}
            state["idempotency"] = legacy
        expired: list[str] = []
        for key, payload in idx.items():
            if not isinstance(key, str) or not isinstance(payload, dict):
                expired.append(key)
                continue
            ts = payload.get("ts", 0)
            if not isinstance(ts, int) or (now - ts) >= ttl:
                expired.append(key)
        for key in expired:
            idx.pop(key, None)
            legacy.pop(key, None)
        if len(idx) > cap:
            ordered = sorted(
                ((k, v) for k, v in idx.items() if isinstance(v, dict)),
                key=lambda kv: int(kv[1].get("ts", 0)) if isinstance(kv[1].get("ts", 0), int) else 0,
            )
            drop = max(0, len(idx) - cap)
            for key, _ in ordered[:drop]:
                idx.pop(key, None)
                legacy.pop(key, None)

    def _prune_token_jti_cache(self, state: Dict[str, Any]) -> None:
        ttl = max(1, int(self._config.token_jti_ttl_seconds))
        cap = max(1, int(self._config.token_jti_max_entries))
        now = int(time.time())
        seen = state.get("token_jti_seen", {})
        if not isinstance(seen, dict):
            seen = {}
            state["token_jti_seen"] = seen
        expired: list[str] = []
        for jti, ts in seen.items():
            if not isinstance(jti, str) or not isinstance(ts, int) or (now - ts) >= ttl:
                expired.append(jti)
        for jti in expired:
            seen.pop(jti, None)
        if len(seen) > cap:
            ordered = sorted((k, int(v)) for k, v in seen.items() if isinstance(v, int))
            drop = max(0, len(seen) - cap)
            for key, _ in ordered[:drop]:
                seen.pop(key, None)

    def _enforce_replay_token_lifecycle(self, *, state: Dict[str, Any], job_id: str, token: str) -> None:
        if not self._config.enforce_replay_token_binding:
            return
        tokens = state.get("replay_tokens", {})
        if not isinstance(tokens, dict):
            raise ValueError("invalid replay token store")
        payload = tokens.get(job_id)
        if not isinstance(payload, dict):
            raise ValueError("missing replay token")
        if payload.get("revoked") is True:
            raise ValueError("replay token revoked")
        minted_at = payload.get("minted_at", 0)
        if not isinstance(minted_at, int):
            raise ValueError("invalid replay token metadata")
        if (int(time.time()) - minted_at) > max(1, int(self._config.replay_token_ttl_seconds)):
            raise ValueError("replay token expired")
        bound_hash = payload.get("bound_token_hash")
        if not isinstance(bound_hash, str) or not bound_hash:
            raise ValueError("invalid replay token metadata")
        if bound_hash != _sha256_text(token):
            raise ValueError("replay token binding mismatch")
        uses = payload.get("uses", 0)
        if not isinstance(uses, int) or uses < 0:
            uses = 0
        uses += 1
        if uses > max(1, int(self._config.replay_token_max_uses)):
            raise ValueError("replay token use limit exceeded")
        payload["uses"] = uses
        tokens[job_id] = payload

    @staticmethod
    def _idempotency_job(state: Dict[str, Any], key: str) -> str:
        meta = state.get("idempotency_meta", {})
        if isinstance(meta, dict):
            payload = meta.get(key)
            if isinstance(payload, dict):
                job_id = payload.get("job_id")
                if isinstance(job_id, str):
                    return job_id
        raw = state.get("idempotency", {})
        if isinstance(raw, dict):
            job = raw.get(key)
            if isinstance(job, str):
                return job
        return ""

    @staticmethod
    def _require_job_locked(state: Dict[str, Any], job_id: str) -> Dict[str, Any]:
        jobs = state.get("jobs", {})
        if not isinstance(jobs, dict) or job_id not in jobs:
            raise ValueError("job_id not found")
        return dict(jobs[job_id])

    def _build_evidence(self, job_id: str) -> Dict[str, Any]:
        root = self._config.root
        conformance = root / "conformance" / "reports" / "latest.json"
        bundle_manifest = _first_existing(
            [
                root / "artifacts" / "bundles" / "hello-core-bundle.sha256",
                root / "dist" / "hello-core-bundle.sha256",
            ]
        )
        repro = _first_existing(
            [
                root / "evidence" / "repro" / "hashes.txt",
                root / "reports" / "repro" / "hashes.txt",
            ]
        )
        return {
            "job_id": job_id,
            "api_version": self._config.api_version,
            "conformance_report_hash": _sha256_file(conformance) if conformance.exists() else "",
            "bundle_manifest_line": bundle_manifest.read_text(encoding="utf-8").strip()
            if bundle_manifest.exists()
            else "",
            "repro_hash_line": repro.read_text(encoding="utf-8").strip() if repro.exists() else "",
        }

    @staticmethod
    def _bump_counter(counter: Dict[str, Any], key: str, limit: int, *, error: str) -> None:
        current = counter.get(key, 0)
        if not isinstance(current, int) or current < 0:
            current = 0
        nxt = current + 1
        if nxt > limit:
            raise ValueError(error)
        counter[key] = nxt

    @staticmethod
    def _enforce_request_size(payload: Dict[str, Any], *, limit: int, error: str) -> None:
        if limit <= 0:
            return
        try:
            encoded = _canonical_json(payload).encode("utf-8")
        except Exception:
            raise ValueError(error) from None
        if len(encoded) > limit:
            raise ValueError(error)

    def _bump_token_quota(
        self,
        state: Dict[str, Any],
        *,
        token: str,
        action: str,
        request_limit: int,
        submit_limit: int | None = None,
        window_limit: int,
        window_seconds: int,
    ) -> None:
        quotas = state["quotas"]
        self._bump_counter(
            quotas["token_requests"],
            token,
            request_limit,
            error="token request quota exceeded",
        )
        if submit_limit is not None:
            self._bump_counter(
                quotas["token_submits"],
                token,
                submit_limit,
                error="token submit quota exceeded",
            )
        self._bump_token_window_quota(
            quotas["token_request_window"],
            token=f"{token}:{action}",
            limit=window_limit,
            window_seconds=window_seconds,
        )

    @staticmethod
    def _bump_token_window_quota(
        counter: Dict[str, Any],
        *,
        token: str,
        limit: int,
        window_seconds: int,
    ) -> None:
        if window_seconds <= 0 or limit <= 0:
            return
        now = int(time.time())
        raw = counter.get(token, [])
        if not isinstance(raw, list):
            raw = []
        recent = [int(ts) for ts in raw if isinstance(ts, int) and (now - ts) < window_seconds]
        if len(recent) >= limit:
            raise ValueError("token burst rate exceeded")
        recent.append(now)
        counter[token] = recent

    def _bump_job_read_quota(self, state: Dict[str, Any], *, job_id: str, limit: int) -> None:
        quotas = state["quotas"]
        self._bump_counter(
            quotas["job_reads"],
            job_id,
            limit,
            error="job read quota exceeded",
        )

    def _bump_job_replay_quota(self, state: Dict[str, Any], *, job_id: str, limit: int) -> None:
        quotas = state["quotas"]
        self._bump_counter(
            quotas["job_replays"],
            job_id,
            limit,
            error="job replay quota exceeded",
        )

    def _record_auth_failure(self, state: Dict[str, Any], *, token: str) -> None:
        quotas = state["quotas"]
        counter = quotas["auth_failures_by_token"]
        current = counter.get(token, 0)
        if not isinstance(current, int) or current < 0:
            current = 0
        nxt = current + 1
        counter[token] = nxt
        threshold = max(1, int(self._config.auth_failure_denylist_threshold))
        if nxt >= threshold:
            cooldown = max(1, int(self._config.auth_failure_denylist_cooldown_seconds))
            quotas["auth_failure_cooldown_until"][token] = int(time.time()) + cooldown

    def _enforce_auth_failure_cooldown(self, state: Dict[str, Any], *, token: str) -> None:
        quotas = state["quotas"]
        now = int(time.time())
        until = quotas.get("auth_failure_cooldown_until", {}).get(token, 0)
        if not isinstance(until, int):
            return
        if until > now:
            raise ValueError("token temporarily denied after auth failures")

    @staticmethod
    def _bump_window_counter(
        counter: Dict[str, Any],
        *,
        key: str,
        limit: int,
        window_seconds: int,
        error: str,
    ) -> None:
        if window_seconds <= 0 or limit <= 0:
            return
        now = int(time.time())
        raw = counter.get(key, [])
        if not isinstance(raw, list):
            raw = []
        recent = [int(ts) for ts in raw if isinstance(ts, int) and (now - ts) < window_seconds]
        if len(recent) >= limit:
            raise ValueError(error)
        recent.append(now)
        counter[key] = recent

    def _bump_replay_window_quota(
        self,
        state: Dict[str, Any],
        *,
        token: str,
        job_id: str,
        token_limit: int,
        job_limit: int,
        cross_token_limit: int,
        window_seconds: int,
    ) -> None:
        quotas = state["quotas"]
        self._bump_window_counter(
            quotas["replay_window_by_token"],
            key=token,
            limit=token_limit,
            window_seconds=window_seconds,
            error="token replay burst exceeded",
        )
        self._bump_window_counter(
            quotas["replay_window_by_job"],
            key=job_id,
            limit=job_limit,
            window_seconds=window_seconds,
            error="job replay burst exceeded",
        )
        self._bump_cross_token_replay_window(
            quotas["replay_window_job_tokens"],
            token=token,
            job_id=job_id,
            limit=cross_token_limit,
            window_seconds=window_seconds,
        )

    @staticmethod
    def _bump_cross_token_replay_window(
        counter: Dict[str, Any],
        *,
        token: str,
        job_id: str,
        limit: int,
        window_seconds: int,
    ) -> None:
        if limit <= 0 or window_seconds <= 0:
            return
        now = int(time.time())
        raw = counter.get(job_id, {})
        if not isinstance(raw, dict):
            raw = {}
        cleaned: Dict[str, list[int]] = {}
        for existing_token, stamps in raw.items():
            if not isinstance(existing_token, str) or not isinstance(stamps, list):
                continue
            keep = [int(ts) for ts in stamps if isinstance(ts, int) and (now - ts) < window_seconds]
            if keep:
                cleaned[existing_token] = keep
        slots = cleaned.get(token, [])
        slots.append(now)
        cleaned[token] = slots
        if len(cleaned) > limit:
            raise ValueError("cross-token replay burst exceeded")
        counter[job_id] = cleaned

    @staticmethod
    def _enforce_replay_cooldown(state: Dict[str, Any], *, job_id: str, cooldown_seconds: int) -> None:
        if cooldown_seconds <= 0:
            return
        now = int(time.time())
        quotas = state["quotas"]
        last_replay = quotas["job_last_replay_ts"].get(job_id, 0)
        if not isinstance(last_replay, int):
            last_replay = 0
        if (now - last_replay) < cooldown_seconds:
            raise ValueError("replay cooldown active")
        quotas["job_last_replay_ts"][job_id] = now
