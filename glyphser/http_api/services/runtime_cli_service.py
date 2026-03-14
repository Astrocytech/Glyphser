from __future__ import annotations

from pathlib import Path
from typing import Any

from glyphser.http_api.controllers.runtime_cli_controller import RuntimeCliController


class RuntimeCliService:
    def __init__(self, controller: RuntimeCliController) -> None:
        self._controller = controller

    def doctor(self, *, run_id: str | None) -> dict[str, Any]:
        return self._controller.doctor(run_id=run_id)

    def setup(
        self,
        *,
        profile: str,
        doctor_manifest: dict[str, Any],
        dry_run: bool,
        offline: bool,
        max_retries: int,
        timeout_sec: int,
        run_id: str | None,
    ) -> dict[str, Any]:
        return self._controller.setup(
            profile=profile,
            doctor_manifest=doctor_manifest,
            dry_run=dry_run,
            offline=offline,
            max_retries=max_retries,
            timeout_sec=timeout_sec,
            run_id=run_id,
        )

    def route_run(self, *, profile: str, doctor_manifest: dict[str, Any], run_id: str | None) -> dict[str, Any]:
        return self._controller.route_run(profile=profile, doctor_manifest=doctor_manifest, run_id=run_id)

    def certify(self, *, profile: str, run_id: str | None) -> dict[str, Any]:
        return self._controller.certify(profile=profile, run_id=run_id)


def runtime_cli_controller_factory(*, work_root: Path) -> RuntimeCliController:
    return RuntimeCliController(work_root=work_root)

