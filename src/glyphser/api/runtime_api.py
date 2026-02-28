"""Versioned runtime API surface for Milestone 18."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


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
    api_version: str = "1.0.0"


class RuntimeApiService:
    """Minimal deterministic API service with file-backed state."""

    def __init__(self, config: RuntimeApiConfig) -> None:
        self._config = config
        self._config.state_path.parent.mkdir(parents=True, exist_ok=True)

    def submit_job(self, payload: Dict[str, Any], token: str, scope: str, idempotency_key: str | None = None) -> Dict[str, Any]:
        self._require_auth(token=token, scope=scope)
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
        return dict(record)

    def status(self, job_id: str, token: str, scope: str) -> Dict[str, Any]:
        self._require_auth(token=token, scope=scope)
        state = self._load_state()
        if job_id not in state["jobs"]:
            raise ValueError("job_id not found")
        return dict(state["jobs"][job_id])

    def evidence(self, job_id: str, token: str, scope: str) -> Dict[str, Any]:
        self._require_auth(token=token, scope=scope)
        _ = self.status(job_id, token=token, scope=scope)
        root = self._config.root
        conformance = root / "conformance" / "reports" / "latest.json"
        bundle_manifest = root / "dist" / "hello-core-bundle.sha256"
        repro = root / "reports" / "repro" / "hashes.txt"
        return {
            "job_id": job_id,
            "api_version": self._config.api_version,
            "conformance_report_hash": _sha256_file(conformance) if conformance.exists() else "",
            "bundle_manifest_line": bundle_manifest.read_text(encoding="utf-8").strip() if bundle_manifest.exists() else "",
            "repro_hash_line": repro.read_text(encoding="utf-8").strip() if repro.exists() else "",
        }

    def replay(self, job_id: str, token: str, scope: str) -> Dict[str, Any]:
        self._require_auth(token=token, scope=scope)
        ev = self.evidence(job_id, token=token, scope=scope)
        bundle_line = ev["bundle_manifest_line"]
        repro_line = ev["repro_hash_line"]
        if not bundle_line or not repro_line:
            return {"job_id": job_id, "api_version": self._config.api_version, "replay_verdict": "FAIL", "reason": "missing evidence"}
        verdict = "PASS" if bundle_line == repro_line else "FAIL"
        return {"job_id": job_id, "api_version": self._config.api_version, "replay_verdict": verdict}

    @staticmethod
    def _require_auth(token: str, scope: str) -> None:
        if not isinstance(token, str) or not token.strip():
            raise ValueError("missing auth token")
        if not isinstance(scope, str) or not scope.strip():
            raise ValueError("missing auth scope")

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

