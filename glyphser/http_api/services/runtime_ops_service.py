from __future__ import annotations

from pathlib import Path
from typing import Any

from glyphser.http_api.controllers.runtime_ops_controller import RuntimeOpsController


class RuntimeOpsService:
    def __init__(self, controller: RuntimeOpsController) -> None:
        self._controller = controller

    def list_ops(self) -> list[str]:
        return self._controller.list_ops()

    def call(self, op: str, request: dict[str, Any]) -> dict[str, Any]:
        return self._controller.call(op, request)

    def checkpoint_save(self, *, state: dict[str, Any], name: str) -> dict[str, Any]:
        return self._controller.checkpoint_save(state=state, name=name)


def runtime_ops_service_factory(*, work_root: Path) -> RuntimeOpsService:
    return RuntimeOpsService(RuntimeOpsController(work_root=work_root))

