from __future__ import annotations

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from glyphser.http_api.deps import get_runtime_cli_service, https_required, load_doctor_manifest
from glyphser.http_api.errors import as_http_exception
from glyphser.http_api.schemas import CertifyRequest, DoctorRequest, RouteRunRequest, SetupRequest
from glyphser.http_api.services.runtime_cli_service import RuntimeCliService

router = APIRouter()


@router.post("/runtime/cli/doctor")
def post_runtime_doctor(
    payload: DoctorRequest,
    _: None = Depends(https_required),
    runtime_cli: RuntimeCliService = Depends(get_runtime_cli_service),
):
    try:
        out = runtime_cli.doctor(run_id=payload.run_id)
        return JSONResponse(status_code=status.HTTP_200_OK, content=out)
    except Exception as exc:
        raise as_http_exception(exc) from exc


@router.post("/runtime/cli/setup")
def post_runtime_setup(
    payload: SetupRequest,
    _: None = Depends(https_required),
    runtime_cli: RuntimeCliService = Depends(get_runtime_cli_service),
):
    try:
        manifest = payload.doctor_manifest
        if manifest is None:
            if not payload.doctor_run_id:
                raise ValueError("doctor_manifest or doctor_run_id required")
            manifest = load_doctor_manifest(doctor_run_id=payload.doctor_run_id)
        out = runtime_cli.setup(
            profile=payload.profile,
            doctor_manifest=manifest,
            dry_run=bool(payload.dry_run),
            offline=bool(payload.offline),
            max_retries=int(payload.max_retries),
            timeout_sec=int(payload.timeout_sec),
            run_id=payload.run_id,
        )
        return JSONResponse(status_code=status.HTTP_200_OK, content=out)
    except Exception as exc:
        raise as_http_exception(exc) from exc


@router.post("/runtime/cli/run")
def post_runtime_run(
    payload: RouteRunRequest,
    _: None = Depends(https_required),
    runtime_cli: RuntimeCliService = Depends(get_runtime_cli_service),
):
    try:
        manifest = payload.doctor_manifest
        if manifest is None:
            if not payload.doctor_run_id:
                raise ValueError("doctor_manifest or doctor_run_id required")
            manifest = load_doctor_manifest(doctor_run_id=payload.doctor_run_id)
        out = runtime_cli.route_run(profile=payload.profile, doctor_manifest=manifest, run_id=payload.run_id)
        return JSONResponse(status_code=status.HTTP_200_OK, content=out)
    except Exception as exc:
        raise as_http_exception(exc) from exc


@router.post("/runtime/cli/certify")
def post_runtime_certify(
    payload: CertifyRequest,
    _: None = Depends(https_required),
    runtime_cli: RuntimeCliService = Depends(get_runtime_cli_service),
):
    try:
        out = runtime_cli.certify(profile=payload.profile, run_id=payload.run_id)
        return JSONResponse(status_code=status.HTTP_200_OK, content=out)
    except Exception as exc:
        raise as_http_exception(exc) from exc

