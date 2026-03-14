from __future__ import annotations

from fastapi import APIRouter

from glyphser.http_api.routes.api_tools import router as api_tools_router
from glyphser.http_api.routes.explorer import router as explorer_router
from glyphser.http_api.routes.misc import router as misc_router
from glyphser.http_api.routes.runtime_cli import router as runtime_cli_router
from glyphser.http_api.routes.runtime_jobs import router as runtime_jobs_router
from glyphser.http_api.routes.runtime_ops import router as runtime_ops_router
from glyphser.http_api.routes.runtime_tools import router as runtime_tools_router
from glyphser.http_api.routes.snapshot import router as snapshot_router
from glyphser.http_api.routes.status import router as status_router
from glyphser.http_api.routes.verify import router as verify_router


class ApiRouter:
    def __init__(self) -> None:
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self) -> None:
        self.router.include_router(status_router)
        self.router.include_router(misc_router)
        self.router.include_router(verify_router)
        self.router.include_router(snapshot_router)
        self.router.include_router(runtime_jobs_router)
        self.router.include_router(runtime_cli_router)
        self.router.include_router(api_tools_router)
        self.router.include_router(runtime_tools_router)
        self.router.include_router(runtime_ops_router)
        self.router.include_router(explorer_router)


router = ApiRouter().router

