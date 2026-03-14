from __future__ import annotations

from typing import Any

from runtime.glyphser.api.error_taxonomy import classify_runtime_api_error
from runtime.glyphser.api.validate_signature import validate_api_signature


class ApiToolsService:
    def validate_signature(self, record: dict[str, Any], allowed_ops: list[Any] | None) -> None:
        validate_api_signature(record, allowed_ops=allowed_ops)

    def classify_error(self, message: str) -> str:
        return classify_runtime_api_error(message)

