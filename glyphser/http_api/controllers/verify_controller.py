from __future__ import annotations

from typing import Any

from glyphser import cli as glyphser_cli
from glyphser.public.verify import verify


class VerifyController:
    def verify_model(self, model: dict[str, Any], input_data: dict[str, Any] | None) -> tuple[str, dict[str, Any]]:
        result = verify(model=model, input_data=input_data or {})
        return result.digest, result.output

    def verify_fixture(self, target: str) -> dict[str, Any]:
        cleaned = (target or "").strip()
        if cleaned != "hello-core":
            raise ValueError("unsupported target")
        return glyphser_cli._verify_hello_core()
