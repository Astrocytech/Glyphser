from __future__ import annotations

from typing import Any

from glyphser.public.runtime import RuntimeService


class RuntimeController:
    def __init__(self, service: RuntimeService) -> None:
        self._service = service

    def submit_job(
        self,
        payload: dict[str, Any],
        *,
        token: str,
        scope: str,
        idempotency_key: str | None,
    ) -> dict[str, Any]:
        return self._service.submit_job(payload=payload, token=token, scope=scope, idempotency_key=idempotency_key)

    def status(self, *, job_id: str, token: str, scope: str) -> dict[str, Any]:
        return self._service.status(job_id=job_id, token=token, scope=scope)

    def evidence(self, *, job_id: str, token: str, scope: str) -> dict[str, Any]:
        return self._service.evidence(job_id=job_id, token=token, scope=scope)

    def replay(self, *, job_id: str, token: str, scope: str) -> dict[str, Any]:
        return self._service.replay(job_id=job_id, token=token, scope=scope)

