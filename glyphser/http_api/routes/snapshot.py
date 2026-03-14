from __future__ import annotations

from fastapi import APIRouter, Depends

from glyphser.http_api.deps import get_snapshot_service, https_required
from glyphser.http_api.errors import as_http_exception
from glyphser.http_api.schemas import (
    SnapshotRequest,
    SnapshotResponse,
    SnapshotWriteRequest,
    SnapshotWriteResponse,
)
from glyphser.http_api.services.snapshot_service import SnapshotService

router = APIRouter()


@router.post("/snapshot", response_model=SnapshotResponse)
def post_snapshot(
    payload: SnapshotRequest,
    _: None = Depends(https_required),
    snapshot_service: SnapshotService = Depends(get_snapshot_service),
) -> SnapshotResponse:
    try:
        digest, snapshot = snapshot_service.snapshot(model=payload.model, input_data=payload.input_data)
        return SnapshotResponse(digest=digest, snapshot=snapshot)
    except Exception as exc:
        raise as_http_exception(exc) from exc


@router.post("/snapshot/write", response_model=SnapshotWriteResponse)
def post_snapshot_write(
    payload: SnapshotWriteRequest,
    _: None = Depends(https_required),
    snapshot_service: SnapshotService = Depends(get_snapshot_service),
) -> SnapshotWriteResponse:
    try:
        digest, out_path = snapshot_service.snapshot_to_disk(
            model=payload.model,
            input_data=payload.input_data,
            name=payload.name,
        )
        return SnapshotWriteResponse(digest=digest, path=str(out_path))
    except Exception as exc:
        raise as_http_exception(exc) from exc

