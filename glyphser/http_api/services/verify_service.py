from __future__ import annotations

from typing import Any

from glyphser.http_api.controllers.verify_controller import VerifyController


class VerifyService:
    def __init__(self, controller: VerifyController) -> None:
        self._controller = controller

    def verify(self, model: dict[str, Any], input_data: dict[str, Any] | None) -> tuple[str, dict[str, Any]]:
        return self._controller.verify_model(model=model, input_data=input_data)

    def verify_fixture(self, target: str) -> dict[str, Any]:
        return self._controller.verify_fixture(target)
