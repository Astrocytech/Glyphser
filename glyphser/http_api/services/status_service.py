from __future__ import annotations

from glyphser.http_api.controllers.status_controller import StatusController


class StatusService:
    def __init__(self, controller: StatusController) -> None:
        self._controller = controller

    def get_status(self) -> str:
        return self._controller.check_status()

