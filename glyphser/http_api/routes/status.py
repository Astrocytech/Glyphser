from __future__ import annotations

from fastapi import APIRouter, Depends

from glyphser.http_api.deps import get_status_service, https_required
from glyphser.http_api.errors import as_http_exception
from glyphser.http_api.schemas import StatusResponse
from glyphser.http_api.services.status_service import StatusService

router = APIRouter()


@router.get("/status", response_model=StatusResponse)
def get_status(
    _: None = Depends(https_required),
    status_service: StatusService = Depends(get_status_service),
) -> StatusResponse:
    try:
        return StatusResponse(message=status_service.get_status())
    except Exception as exc:  # pragma: no cover
        raise as_http_exception(exc) from exc

