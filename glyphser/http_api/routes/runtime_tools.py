from __future__ import annotations

from fastapi import APIRouter, Depends

from glyphser.http_api.deps import get_runtime_tools_service, https_required
from glyphser.http_api.errors import as_http_exception
from glyphser.http_api.schemas import (
    CertificateWriteRequest,
    ContractValidateRequest,
    EvidenceValidateRequest,
    InterfaceHashRequest,
    IrValidateRequest,
    LoadDriverRequest,
    NextBatchRequest,
    TraceHashRequest,
    TraceHashResponse,
    TraceWriteRequest,
)
from glyphser.http_api.services.runtime_tools_service import RuntimeToolsService

router = APIRouter()


@router.post("/runtime/tools/ir/validate")
def post_ir_validate(
    payload: IrValidateRequest,
    _: None = Depends(https_required),
    tools: RuntimeToolsService = Depends(get_runtime_tools_service),
):
    try:
        return tools.ir_validate(payload.ir_dag)
    except Exception as exc:
        raise as_http_exception(exc) from exc


@router.post("/runtime/tools/trace/hash", response_model=TraceHashResponse)
def post_trace_hash(
    payload: TraceHashRequest,
    _: None = Depends(https_required),
    tools: RuntimeToolsService = Depends(get_runtime_tools_service),
) -> TraceHashResponse:
    try:
        return TraceHashResponse(trace_final_hash=tools.trace_hash(payload.records))
    except Exception as exc:
        raise as_http_exception(exc) from exc


@router.post("/runtime/tools/trace/write")
def post_trace_write(
    payload: TraceWriteRequest,
    _: None = Depends(https_required),
    tools: RuntimeToolsService = Depends(get_runtime_tools_service),
):
    try:
        return tools.write_trace(records=payload.records, name=payload.name)
    except Exception as exc:
        raise as_http_exception(exc) from exc


@router.post("/runtime/tools/certificate/write")
def post_certificate_write(
    payload: CertificateWriteRequest,
    _: None = Depends(https_required),
    tools: RuntimeToolsService = Depends(get_runtime_tools_service),
):
    try:
        return tools.write_execution_certificate(evidence=payload.evidence, name=payload.name)
    except Exception as exc:
        raise as_http_exception(exc) from exc


@router.get("/runtime/tools/backend/routes")
def get_backend_routes(
    _: None = Depends(https_required),
    tools: RuntimeToolsService = Depends(get_runtime_tools_service),
):
    try:
        return tools.route_catalog()
    except Exception as exc:
        raise as_http_exception(exc) from exc


@router.post("/runtime/tools/backend/policy")
def post_backend_policy(
    payload: LoadDriverRequest,
    _: None = Depends(https_required),
    tools: RuntimeToolsService = Depends(get_runtime_tools_service),
):
    try:
        return tools.route_policy(payload.request)
    except Exception as exc:
        raise as_http_exception(exc) from exc


@router.post("/runtime/tools/backend/load-driver")
def post_load_driver(
    payload: LoadDriverRequest,
    _: None = Depends(https_required),
    tools: RuntimeToolsService = Depends(get_runtime_tools_service),
):
    try:
        return tools.load_driver(payload.request)
    except Exception as exc:
        raise as_http_exception(exc) from exc


@router.post("/runtime/tools/contract/validate")
def post_contract_validate(
    payload: ContractValidateRequest,
    _: None = Depends(https_required),
    tools: RuntimeToolsService = Depends(get_runtime_tools_service),
):
    try:
        return tools.contract_validate(payload.ir_dag, driver_request=payload.driver_request, mode=payload.mode)
    except Exception as exc:
        raise as_http_exception(exc) from exc


@router.post("/runtime/tools/cert/evidence-validate")
def post_evidence_validate(
    payload: EvidenceValidateRequest,
    _: None = Depends(https_required),
    tools: RuntimeToolsService = Depends(get_runtime_tools_service),
):
    try:
        return tools.evidence_validate(payload.request)
    except Exception as exc:
        raise as_http_exception(exc) from exc


@router.post("/runtime/tools/data/next-batch")
def post_next_batch(
    payload: NextBatchRequest,
    _: None = Depends(https_required),
    tools: RuntimeToolsService = Depends(get_runtime_tools_service),
):
    try:
        return tools.next_batch(payload.dataset, payload.cursor, payload.batch_size)
    except Exception as exc:
        raise as_http_exception(exc) from exc


@router.post("/runtime/tools/registry/interface-hash")
def post_interface_hash(
    payload: InterfaceHashRequest,
    _: None = Depends(https_required),
    tools: RuntimeToolsService = Depends(get_runtime_tools_service),
):
    try:
        return tools.interface_hash(payload.registry)
    except Exception as exc:
        raise as_http_exception(exc) from exc


@router.get("/runtime/tools/registry/api-interfaces")
def get_api_interfaces(
    _: None = Depends(https_required),
    tools: RuntimeToolsService = Depends(get_runtime_tools_service),
):
    try:
        return {"items": tools.api_interfaces_from_repo()}
    except Exception as exc:
        raise as_http_exception(exc) from exc

