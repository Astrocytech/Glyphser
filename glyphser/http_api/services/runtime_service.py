from __future__ import annotations

from functools import lru_cache

from glyphser import RuntimeApiConfig, RuntimeService
from glyphser.http_api.config.settings import settings
from glyphser.http_api.controllers.runtime_controller import RuntimeController


@lru_cache(maxsize=1)
def runtime_service_singleton() -> RuntimeService:
    config = RuntimeApiConfig(
        root=settings.runtime_root,
        state_path=settings.runtime_state_path,
        audit_log_path=settings.runtime_audit_log_path,
    )
    return RuntimeService(config)


def runtime_controller() -> RuntimeController:
    return RuntimeController(runtime_service_singleton())

