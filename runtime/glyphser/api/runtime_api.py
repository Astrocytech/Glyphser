"""Versioned runtime API surface for Milestone 18."""

from __future__ import annotations

import hashlib
import json
import re
import threading
import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from runtime.glyphser.security.audit import append_event
from runtime.glyphser.security.authz import authorize

_MAX_PAYLOAD_DEPTH = 16
_MAX_PAYLOAD_ITEMS = 50_000
_MAX_PAYLOAD_BYTES = 128 * 1024
_MAX_IDEMPOTENCY_KEY_LENGTH = 128
_MAX_SCOPE_LENGTH = 64
_MAX_TOKEN_LENGTH = 256

_JOB_ID_RE = re.compile(r"^[0-9a-f]{24}$")
_PAYLOAD_KEY_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,64}$")
_IDEMPOTENCY_KEY_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


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


def _validate_payload(payload: Dict[str, Any]) -> None:
    if not isinstance(payload, dict):
        raise ValueError("payload must be dict")
    if len(payload) > 256:
        raise ValueError("payload has too many top-level keys")

    stack: list[tuple[Any, int]] = [(payload, 0)]
    seen_items = 0
    while stack:
        current, depth = stack.pop()
        seen_items += 1
        if seen_items > _MAX_PAYLOAD_ITEMS:
            raise ValueError("payload too complex")
        if depth > _MAX_PAYLOAD_DEPTH:
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


class RuntimeApiService:
    """Minimal deterministic API service with file-backed state."""

    def __init__(self, config: RuntimeApiConfig) -> None:
        self._config = config
        self._lock = threading.RLock()
        self._config.state_path.parent.mkdir(parents=True, exist_ok=True)

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
        _validate_scope(scope, expected="jobs:write")
        self._require_auth_with_tracking(token=token, action="jobs:write", scope=scope, job_id="")
        _validate_payload(payload)
        _validate_submit_payload_schema(payload)
        if idempotency_key and len(idempotency_key) > _MAX_IDEMPOTENCY_KEY_LENGTH:
            raise ValueError("idempotency_key too long")
        if idempotency_key and not _IDEMPOTENCY_KEY_RE.match(idempotency_key):
            raise ValueError("idempotency_key has invalid characters")
        with self._lock:
            state = self._load_state()
            self._bump_token_quota(
                state,
                token=token,
                request_limit=self._config.max_requests_per_token,
                submit_limit=self._config.max_submits_per_token,
                window_limit=self._config.max_requests_per_window,
                window_seconds=self._config.request_window_seconds,
            )

            if idempotency_key:
                existing = state["idempotency"].get(idempotency_key)
                if existing:
                    out = dict(state["jobs"][existing])
                    _validate_against_schema("submit_response", out)
                    self._audit("status", token=token, job_id=existing, scope=scope)
                    return out

            payload_text = _canonical_json(payload)
            if len(payload_text.encode("utf-8")) > _MAX_PAYLOAD_BYTES:
                raise ValueError("payload too large")
            basis = f"job:{idempotency_key or payload_text}"
            job_id = _sha256_text(basis)[:24]
            trace_id = _sha256_text(f"trace:{job_id}:{payload_text}")[:32]
            record = {
                "job_id": job_id,
                "trace_id": trace_id,
                "status": "accepted",
                "api_version": self._config.api_version,
                "payload_hash": _sha256_text(payload_text),
                "idempotency_key": idempotency_key or "",
            }
            state["jobs"][job_id] = record
            if idempotency_key:
                state["idempotency"][idempotency_key] = job_id
            self._save_state(state)
            self._audit("submit", token=token, job_id=job_id, scope=scope)
            _validate_against_schema("submit_response", record)
            return dict(record)

    def status(self, job_id: str, token: str, scope: str) -> Dict[str, Any]:
        _validate_against_schema("status_request", {"job_id": job_id, "token": token, "scope": scope})
        _validate_scope(scope, expected="jobs:read")
        _validate_job_id(job_id)
        self._require_auth_with_tracking(token=token, action="jobs:read", scope=scope, job_id=job_id)
        with self._lock:
            state = self._load_state()
            self._bump_token_quota(
                state,
                token=token,
                request_limit=self._config.max_requests_per_token,
                window_limit=self._config.max_requests_per_window,
                window_seconds=self._config.request_window_seconds,
            )
            out = self._require_job_locked(state, job_id)
            self._bump_job_read_quota(state, job_id=job_id, limit=self._config.max_reads_per_job)
            self._save_state(state)
            self._audit("status", token=token, job_id=job_id, scope=scope)
            _validate_against_schema("status_response", out)
            return out

    def evidence(self, job_id: str, token: str, scope: str) -> Dict[str, Any]:
        _validate_against_schema("evidence_request", {"job_id": job_id, "token": token, "scope": scope})
        _validate_scope(scope, expected="evidence:read")
        _validate_job_id(job_id)
        self._require_auth_with_tracking(token=token, action="evidence:read", scope=scope, job_id=job_id)
        with self._lock:
            state = self._load_state()
            self._bump_token_quota(
                state,
                token=token,
                request_limit=self._config.max_requests_per_token,
                window_limit=self._config.max_requests_per_window,
                window_seconds=self._config.request_window_seconds,
            )
            _ = self._require_job_locked(state, job_id)
            self._bump_job_read_quota(state, job_id=job_id, limit=self._config.max_reads_per_job)
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
        _validate_scope(scope, expected="replay:run")
        _validate_job_id(job_id)
        self._require_auth_with_tracking(token=token, action="replay:run", scope=scope, job_id=job_id)
        with self._lock:
            state = self._load_state()
            self._bump_token_quota(
                state,
                token=token,
                request_limit=self._config.max_requests_per_token,
                window_limit=self._config.max_requests_per_window,
                window_seconds=self._config.request_window_seconds,
            )
            _ = self._require_job_locked(state, job_id)
            self._bump_job_read_quota(state, job_id=job_id, limit=self._config.max_reads_per_job)
            self._enforce_replay_cooldown(state, job_id=job_id, cooldown_seconds=self._config.replay_cooldown_seconds)
            self._bump_job_replay_quota(state, job_id=job_id, limit=self._config.max_replays_per_job)
            self._save_state(state)
            ev = self._build_evidence(job_id)
            bundle_line = ev["bundle_manifest_line"]
            repro_line = ev["repro_hash_line"]
            if not bundle_line or not repro_line:
                out = {
                    "job_id": job_id,
                    "api_version": self._config.api_version,
                    "replay_verdict": "FAIL",
                    "reason": "missing evidence",
                }
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
    def _roles_from_token(token: str) -> list[str]:
        if token.startswith("role:"):
            return [token.split(":", 1)[1]]
        return ["admin"]

    def _require_auth(self, token: str, action: str) -> None:
        if not isinstance(token, str) or not token.strip():
            raise ValueError("missing auth token")
        if len(token) > _MAX_TOKEN_LENGTH:
            raise ValueError("token too long")
        roles = self._roles_from_token(token)
        if not authorize(action, roles):
            raise ValueError(f"unauthorized action: {action}")

    def _require_auth_with_tracking(self, *, token: str, action: str, scope: str, job_id: str) -> None:
        try:
            self._require_auth(token=token, action=action)
        except ValueError:
            with self._lock:
                state = self._load_state()
                self._record_auth_failure(state, token=token)
                self._save_state(state)
            self._audit("auth_failure", token=token, job_id=job_id, scope=scope)
            raise

    def _audit(
        self,
        operation: str,
        token: str,
        job_id: str,
        scope: str,
        replay_verdict: str = "",
    ) -> None:
        path = self._config.audit_log_path or self._config.state_path.parent / "audit.log.jsonl"
        append_event(
            path,
            {
                "operation": operation,
                "job_id": job_id,
                "scope": scope,
                "role_token": token,
                "replay_verdict": replay_verdict,
            },
        )

    def _load_state(self) -> Dict[str, Any]:
        if not self._config.state_path.exists():
            return {
                "jobs": {},
                "idempotency": {},
                "quotas": {
                    "token_requests": {},
                    "token_submits": {},
                    "job_reads": {},
                    "job_replays": {},
                    "job_last_replay_ts": {},
                    "token_request_window": {},
                    "auth_failures_by_token": {},
                },
            }
        data = json.loads(self._config.state_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("invalid state")
        data.setdefault("jobs", {})
        data.setdefault("idempotency", {})
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
        return data

    def _save_state(self, state: Dict[str, Any]) -> None:
        self._config.state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")

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

    def _bump_token_quota(
        self,
        state: Dict[str, Any],
        *,
        token: str,
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
            token=token,
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
        counter[token] = current + 1

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
