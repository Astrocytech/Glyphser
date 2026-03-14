from __future__ import annotations

from pathlib import Path
from typing import Any

from glyphser.http_api.controllers.explorer_controller import ExplorerController


class ExplorerService:
    def __init__(self, controller: ExplorerController) -> None:
        self._controller = controller

    def roots(self) -> dict[str, str]:
        return self._controller.roots()

    def list_dir(self, *, root: str, path: str) -> list[dict[str, Any]]:
        return self._controller.list_dir(root_label=root, rel_path=path)

    def read_text(self, *, root: str, path: str) -> str:
        return self._controller.read_text(root_label=root, rel_path=path)


def explorer_controller_factory(*, repo_root: Path, work_root: Path) -> ExplorerController:
    return ExplorerController(repo_root=repo_root, work_root=work_root)

