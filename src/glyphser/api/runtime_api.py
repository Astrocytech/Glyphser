"""Versioned runtime API surface for Milestone 18."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from src.glyphser.security.audit import append_event
from src.glyphser.security.authz import authorize


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


@dataclass(frozen=True)
class RuntimeApiConfig:
    root: Path
    state_path: Path
    audit_log_path: Path | None = None
    api_version: str = "1.0.0"


class RuntimeApiService:
    """Minimal deterministic API service with file-backed state."""

    def __init__(self, config: RuntimeApiConfig) -> None:
        self._config = config
        self._config.state_path.parent.mkdir(parents=True, exist_ok=True)

    def submit_job(self, payload: Dict[str, Any], token: str, scope: str, idempotency_key: str | None = None) -> Dict[str, Any]:
        self._require_auth(token=token, action="jobs:write")
        state = self._load_state()

        if idempotency_key:
            existing = state["idempotency"].get(idempotency_key)
            if existing:
                return self.status(existing, token=token, scope=scope)

        payload_text = _canonical_json(payload)
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
        return dict(record)

    def status(self, job_id: str, token: str, scope: str) -> Dict[str, Any]:
        self._require_auth(token=token, action="jobs:read")
        state = self._load_state()
        if job_id not in state["jobs"]:
            raise ValueError("job_id not found")
        out = dict(state["jobs"][job_id])
        self._audit("status", token=token, job_id=job_id, scope=scope)
        return out

    def evidence(self, job_id: str, token: str, scope: str) -> Dict[str, Any]:
        self._require_auth(token=token, action="evidence:read")
        _ = self.status(job_id, token=token, scope=scope)
        root = self._config.root
        conformance = root / "conformance" / "reports" / "latest.json"
        bundle_manifest = _first_existing(
            [root / "artifacts" / "bundles" / "hello-core-bundle.sha256", root / "dist" / "hello-core-bundle.sha256"]
        )
        repro = _first_existing([root / "evidence" / "repro" / "hashes.txt", root / "reports" / "repro" / "hashes.txt"])
        out = {
            "job_id": job_id,
            "api_version": self._config.api_version,
            "conformance_report_hash": _sha256_file(conformance) if conformance.exists() else "",
            "bundle_manifest_line": bundle_manifest.read_text(encoding="utf-8").strip() if bundle_manifest.exists() else "",
            "repro_hash_line": repro.read_text(encoding="utf-8").strip() if repro.exists() else "",
        }
        self._audit("evidence", token=token, job_id=job_id, scope=scope)
        return out

    def replay(self, job_id: str, token: str, scope: str) -> Dict[str, Any]:
        self._require_auth(token=token, action="replay:run")
        ev = self.evidence(job_id, token=token, scope=scope)
        bundle_line = ev["bundle_manifest_line"]
        repro_line = ev["repro_hash_line"]
        if not bundle_line or not repro_line:
            out = {"job_id": job_id, "api_version": self._config.api_version, "replay_verdict": "FAIL", "reason": "missing evidence"}
            self._audit("replay", token=token, job_id=job_id, scope=scope, replay_verdict="FAIL")
            return out
        verdict = "PASS" if bundle_line == repro_line else "FAIL"
        out = {"job_id": job_id, "api_version": self._config.api_version, "replay_verdict": verdict}
        self._audit("replay", token=token, job_id=job_id, scope=scope, replay_verdict=verdict)
        return out

    @staticmethod
    def _roles_from_token(token: str) -> list[str]:
        if token.startswith("role:"):
            return [token.split(":", 1)[1]]
        return ["admin"]

    def _require_auth(self, token: str, action: str) -> None:
        if not isinstance(token, str) or not token.strip():
            raise ValueError("missing auth token")
        roles = self._roles_from_token(token)
        if not authorize(action, roles):
            raise ValueError(f"unauthorized action: {action}")

    def _audit(self, operation: str, token: str, job_id: str, scope: str, replay_verdict: str = "") -> None:
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
            return {"jobs": {}, "idempotency": {}}
        data = json.loads(self._config.state_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("invalid state")
        data.setdefault("jobs", {})
        data.setdefault("idempotency", {})
        return data

    def _save_state(self, state: Dict[str, Any]) -> None:
        self._config.state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
