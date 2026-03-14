from __future__ import annotations

import json

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from glyphser.http_api.config.settings import settings
from glyphser.http_api.deps import get_runtime_jobs_controller, https_required
from glyphser.http_api.errors import as_http_exception
from glyphser.http_api.schemas import RuntimeJobRequest, RuntimeSubmitRequest

router = APIRouter()


@router.post("/runtime/jobs/submit")
def post_runtime_submit(
    payload: RuntimeSubmitRequest,
    _: None = Depends(https_required),
):
    try:
        controller = get_runtime_jobs_controller()
        out = controller.submit_job(
            payload=payload.payload,
            token=payload.token,
            scope=payload.scope,
            idempotency_key=payload.idempotency_key,
        )
        return JSONResponse(status_code=status.HTTP_200_OK, content=out)
    except Exception as exc:
        raise as_http_exception(exc) from exc


@router.post("/runtime/jobs/status")
def post_runtime_status(
    payload: RuntimeJobRequest,
    _: None = Depends(https_required),
):
    try:
        controller = get_runtime_jobs_controller()
        out = controller.status(job_id=payload.job_id, token=payload.token, scope=payload.scope)
        return JSONResponse(status_code=status.HTTP_200_OK, content=out)
    except Exception as exc:
        raise as_http_exception(exc) from exc


@router.post("/runtime/jobs/evidence")
def post_runtime_evidence(
    payload: RuntimeJobRequest,
    _: None = Depends(https_required),
):
    try:
        controller = get_runtime_jobs_controller()
        out = controller.evidence(job_id=payload.job_id, token=payload.token, scope=payload.scope)
        return JSONResponse(status_code=status.HTTP_200_OK, content=out)
    except Exception as exc:
        raise as_http_exception(exc) from exc


@router.post("/runtime/jobs/replay")
def post_runtime_replay(
    payload: RuntimeJobRequest,
    _: None = Depends(https_required),
):
    try:
        controller = get_runtime_jobs_controller()
        out = controller.replay(job_id=payload.job_id, token=payload.token, scope=payload.scope)
        return JSONResponse(status_code=status.HTTP_200_OK, content=out)
    except Exception as exc:
        raise as_http_exception(exc) from exc


@router.get("/runtime/jobs/state")
def get_runtime_jobs_state(_: None = Depends(https_required)):
    try:
        path = settings.runtime_state_path
        if not path.exists():
            return {"state_path": str(path), "exists": False, "jobs": [], "quotas": {}}
        state = json.loads(path.read_text(encoding="utf-8"))
        jobs = state.get("jobs", {}) if isinstance(state, dict) else {}
        quotas = state.get("quotas", {}) if isinstance(state, dict) else {}
        job_rows = []
        if isinstance(jobs, dict):
            for job_id, rec in jobs.items():
                if not isinstance(rec, dict):
                    continue
                job_rows.append(
                    {
                        "job_id": job_id,
                        "status": rec.get("status"),
                        "trace_id": rec.get("trace_id"),
                        "api_version": rec.get("api_version"),
                    }
                )
        safe_quotas = quotas if isinstance(quotas, dict) else {}
        return {"state_path": str(path), "exists": True, "jobs": sorted(job_rows, key=lambda r: r["job_id"]), "quotas": safe_quotas}
    except Exception as exc:
        raise as_http_exception(exc) from exc


@router.get("/runtime/jobs/audit")
def get_runtime_jobs_audit(limit: int = 200, _: None = Depends(https_required)):
    try:
        limit = max(1, min(int(limit), 2000))
        audit_path = settings.runtime_state_path.parent / "audit.log.jsonl"
        if not audit_path.exists():
            return {"audit_path": str(audit_path), "exists": False, "events": []}
        lines = audit_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        tail = lines[-limit:]
        events = []
        for line in tail:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                obj = {"raw": line}
            events.append(obj)
        return {"audit_path": str(audit_path), "exists": True, "events": events}
    except Exception as exc:
        raise as_http_exception(exc) from exc

