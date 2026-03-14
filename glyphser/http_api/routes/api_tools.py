from __future__ import annotations

from fastapi import APIRouter, Depends

from glyphser.http_api.deps import get_api_tools_service, https_required
from glyphser.http_api.errors import as_http_exception
from glyphser.http_api.schemas import (
    ApiSignatureValidateRequest,
    ApiSignatureValidateResponse,
    ErrorClassifyRequest,
    ErrorClassifyResponse,
)
from glyphser.http_api.services.api_tools_service import ApiToolsService

router = APIRouter()


@router.post("/runtime/api-tools/validate-signature", response_model=ApiSignatureValidateResponse)
def post_validate_signature(
    payload: ApiSignatureValidateRequest,
    _: None = Depends(https_required),
    tools: ApiToolsService = Depends(get_api_tools_service),
) -> ApiSignatureValidateResponse:
    try:
        tools.validate_signature(payload.record, payload.allowed_ops)
        return ApiSignatureValidateResponse()
    except Exception as exc:
        raise as_http_exception(exc) from exc


@router.post("/runtime/api-tools/classify-error", response_model=ErrorClassifyResponse)
def post_classify_error(
    payload: ErrorClassifyRequest,
    _: None = Depends(https_required),
    tools: ApiToolsService = Depends(get_api_tools_service),
) -> ErrorClassifyResponse:
    try:
        return ErrorClassifyResponse(code=tools.classify_error(payload.message))
    except Exception as exc:  # pragma: no cover
        raise as_http_exception(exc) from exc

