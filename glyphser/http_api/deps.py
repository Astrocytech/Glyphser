from __future__ import annotations

import json
from pathlib import Path

from fastapi import Depends, Request

from glyphser.http_api.config.settings import settings
from glyphser.http_api.controllers.explorer_controller import ExplorerController
from glyphser.http_api.controllers.snapshot_controller import SnapshotController
from glyphser.http_api.controllers.status_controller import StatusController
from glyphser.http_api.controllers.verify_controller import VerifyController
from glyphser.http_api.services.api_tools_service import ApiToolsService
from glyphser.http_api.services.explorer_service import ExplorerService, explorer_controller_factory
from glyphser.http_api.services.runtime_cli_service import RuntimeCliService, runtime_cli_controller_factory
from glyphser.http_api.services.runtime_ops_service import RuntimeOpsService, runtime_ops_service_factory
from glyphser.http_api.services.runtime_service import runtime_controller
from glyphser.http_api.services.runtime_tools_service import RuntimeToolsService, runtime_tools_service_factory
from glyphser.http_api.services.snapshot_service import SnapshotService
from glyphser.http_api.services.status_service import StatusService
from glyphser.http_api.services.verify_service import VerifyService


def https_required(request: Request) -> None:
    if settings.require_https and request.url.scheme != "https":
        raise PermissionError("HTTPS required")


def repo_root() -> Path:
    return settings.runtime_root.resolve()


def get_status_controller() -> StatusController:
    return StatusController()


def get_verify_controller() -> VerifyController:
    return VerifyController()


def get_snapshot_controller() -> SnapshotController:
    return SnapshotController()


def get_status_service(controller: StatusController = Depends(get_status_controller)) -> StatusService:
    return StatusService(controller)


def get_verify_service(controller: VerifyController = Depends(get_verify_controller)) -> VerifyService:
    return VerifyService(controller)


def get_snapshot_service(controller: SnapshotController = Depends(get_snapshot_controller)) -> SnapshotService:
    return SnapshotService(controller, snapshot_root=settings.snapshot_root)


def get_runtime_cli_service() -> RuntimeCliService:
    controller = runtime_cli_controller_factory(work_root=settings.work_root)
    return RuntimeCliService(controller)


def get_api_tools_service() -> ApiToolsService:
    return ApiToolsService()


def get_explorer_service() -> ExplorerService:
    controller: ExplorerController = explorer_controller_factory(repo_root=repo_root(), work_root=settings.work_root)
    return ExplorerService(controller)


def get_runtime_tools_service() -> RuntimeToolsService:
    return runtime_tools_service_factory(repo_root=repo_root(), work_root=settings.work_root)


def get_runtime_ops_service() -> RuntimeOpsService:
    return runtime_ops_service_factory(work_root=settings.work_root)


def get_runtime_jobs_controller():
    return runtime_controller()


def load_doctor_manifest(*, doctor_run_id: str) -> dict:
    rid = (doctor_run_id or "").strip()
    if not rid or "/" in rid or "\\" in rid:
        raise ValueError("doctor_run_id invalid")
    path = (settings.work_root / "doctor" / rid / "doctor.json").resolve()
    root = settings.work_root.resolve()
    if root not in path.parents:
        raise PermissionError("doctor manifest path escapes workspace")
    if not path.exists():
        raise ValueError("doctor manifest not found; run /runtime/cli/doctor first")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("doctor manifest invalid")
    return payload

