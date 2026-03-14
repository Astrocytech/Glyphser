from __future__ import annotations

import json

from fastapi import APIRouter, Depends

from glyphser.http_api.config.settings import settings
from glyphser.http_api.deps import https_required, repo_root
from glyphser.http_api.errors import as_http_exception

router = APIRouter()


@router.get("/info")
def get_info(_: None = Depends(https_required)):
    return {
        "service": "glyphser-http-api",
        "work_root": str(settings.work_root),
        "snapshot_root": str(settings.snapshot_root),
        "runtime_api_root": str(settings.runtime_root),
        "runtime_api_state_path": str(settings.runtime_state_path),
    }


@router.get("/runtime/api/schemas")
def get_runtime_api_schemas(_: None = Depends(https_required)):
    try:
        schema_path = repo_root() / "runtime" / "glyphser" / "api" / "schemas" / "runtime_api_schemas.json"
        return json.loads(schema_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise as_http_exception(exc) from exc


@router.get("/conformance/latest")
def get_conformance_latest(_: None = Depends(https_required)):
    try:
        root = repo_root()
        report_path = root / "conformance" / "reports" / "latest.json"
        interface_hash_path = root / "specs" / "contracts" / "interface_hash.json"
        return {
            "report_path": str(report_path),
            "interface_hash_path": str(interface_hash_path),
            "report": json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else None,
            "interface_hash": json.loads(interface_hash_path.read_text(encoding="utf-8"))
            if interface_hash_path.exists()
            else None,
        }
    except Exception as exc:
        raise as_http_exception(exc) from exc

