from __future__ import annotations

from fastapi import APIRouter, Depends

from glyphser.http_api.deps import get_runtime_ops_service, https_required
from glyphser.http_api.errors import as_http_exception
from glyphser.http_api.schemas import CheckpointSaveRequest, GenericOpRequest
from glyphser.http_api.services.runtime_ops_service import RuntimeOpsService

router = APIRouter()


@router.get("/runtime/ops")
def get_runtime_ops(
    _: None = Depends(https_required),
    ops: RuntimeOpsService = Depends(get_runtime_ops_service),
):
    try:
        return {"ops": ops.list_ops()}
    except Exception as exc:
        raise as_http_exception(exc) from exc


@router.post("/runtime/ops/{op}")
def post_runtime_op(
    op: str,
    payload: GenericOpRequest,
    _: None = Depends(https_required),
    ops: RuntimeOpsService = Depends(get_runtime_ops_service),
):
    try:
        return ops.call(op, payload.request)
    except Exception as exc:
        raise as_http_exception(exc) from exc


@router.post("/runtime/checkpoint/save")
def post_checkpoint_save(
    payload: CheckpointSaveRequest,
    _: None = Depends(https_required),
    ops: RuntimeOpsService = Depends(get_runtime_ops_service),
):
    try:
        return ops.checkpoint_save(state=payload.state, name=payload.name)
    except Exception as exc:
        raise as_http_exception(exc) from exc

