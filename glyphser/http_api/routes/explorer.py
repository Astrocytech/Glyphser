from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from glyphser.http_api.deps import get_explorer_service, https_required
from glyphser.http_api.errors import as_http_exception
from glyphser.http_api.schemas import ExplorerListResponse, ExplorerReadResponse
from glyphser.http_api.services.explorer_service import ExplorerService

router = APIRouter()


@router.get("/explorer/roots")
def get_explorer_roots(
    _: None = Depends(https_required),
    explorer: ExplorerService = Depends(get_explorer_service),
):
    try:
        return JSONResponse(content=explorer.roots())
    except Exception as exc:  # pragma: no cover
        raise as_http_exception(exc) from exc


@router.get("/explorer/list", response_model=ExplorerListResponse)
def get_explorer_list(
    root: str,
    path: str = ".",
    _: None = Depends(https_required),
    explorer: ExplorerService = Depends(get_explorer_service),
) -> ExplorerListResponse:
    try:
        entries = explorer.list_dir(root=root, path=path)
        return ExplorerListResponse(root=root, path=path, entries=entries)
    except Exception as exc:
        raise as_http_exception(exc) from exc


@router.get("/explorer/read", response_model=ExplorerReadResponse)
def get_explorer_read(
    root: str,
    path: str,
    _: None = Depends(https_required),
    explorer: ExplorerService = Depends(get_explorer_service),
) -> ExplorerReadResponse:
    try:
        content = explorer.read_text(root=root, path=path)
        return ExplorerReadResponse(root=root, path=path, content=content)
    except Exception as exc:
        raise as_http_exception(exc) from exc

