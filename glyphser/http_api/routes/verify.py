from __future__ import annotations

from fastapi import APIRouter, Depends

from glyphser.http_api.deps import get_verify_service, https_required
from glyphser.http_api.errors import as_http_exception
from glyphser.http_api.schemas import VerifyFixtureResponse, VerifyRequest, VerifyResponse
from glyphser.http_api.services.verify_service import VerifyService

router = APIRouter()


@router.get("/verify/targets")
def get_verify_targets(_: None = Depends(https_required)):
    return {"targets": ["hello-core"]}


@router.post("/verify")
def post_verify(
    payload: VerifyRequest,
    _: None = Depends(https_required),
    verify_service: VerifyService = Depends(get_verify_service),
):
    try:
        if payload.model is not None:
            digest, output = verify_service.verify(model=payload.model, input_data=payload.input_data)
            return VerifyResponse(digest=digest, output=output)

        fixture_payload = verify_service.verify_fixture(payload.target or "")
        try:
            VerifyFixtureResponse(**fixture_payload)
        except Exception:
            pass
        return fixture_payload
    except Exception as exc:
        raise as_http_exception(exc) from exc

