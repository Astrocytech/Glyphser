from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from glyphser.http_api.config.settings import settings
from glyphser.http_api.deps import https_required
from glyphser.http_api.errors import as_http_exception


router = APIRouter()


class RunRecord(BaseModel):
    id: str
    status: str
    started_at: str
    finished_at: str | None = None
    summary: str | None = None


class RunDetails(RunRecord):
    inputs: dict[str, Any] | None = None
    artifacts: list[dict[str, Any]] | None = None


def _get_runs_dir() -> Path:
    return settings.work_root / "runs"


def _list_runs() -> list[dict[str, Any]]:
    runs_dir = _get_runs_dir()
    if not runs_dir.exists():
        return []
    
    runs = []
    for run_dir in runs_dir.iterdir():
        if not run_dir.is_dir():
            continue
        run_json = run_dir / "run.json"
        if run_json.exists():
            try:
                runs.append(json.loads(run_json.read_text(encoding="utf-8")))
            except Exception:
                continue
    return sorted(runs, key=lambda r: r.get("started_at", ""), reverse=True)


def _get_run(run_id: str) -> dict[str, Any] | None:
    runs_dir = _get_runs_dir()
    run_dir = runs_dir / run_id
    if not run_dir.exists():
        return None
    run_json = run_dir / "run.json"
    if not run_json.exists():
        return None
    try:
        return json.loads(run_json.read_text(encoding="utf-8"))
    except Exception:
        return None


def _list_artifacts(run_id: str) -> list[dict[str, Any]]:
    run = _get_run(run_id)
    if not run:
        return []
    return run.get("artifacts", [])


def _get_artifact_content(run_id: str, path: str) -> str | None:
    runs_dir = _get_runs_dir()
    artifact_path = runs_dir / run_id / "artifacts" / path
    if not artifact_path.exists():
        return None
    try:
        return artifact_path.read_text(encoding="utf-8")
    except Exception:
        return None


@router.get("/runs", response_model=list[RunRecord])
def get_runs(_: None = Depends(https_required)):
    try:
        runs = _list_runs()
        return [
            RunRecord(
                id=r["id"],
                status=r.get("status", "unknown"),
                started_at=r.get("started_at", ""),
                finished_at=r.get("finished_at"),
                summary=r.get("summary"),
            )
            for r in runs
        ]
    except Exception as exc:
        raise as_http_exception(exc) from exc


@router.get("/runs/{run_id}", response_model=RunDetails)
def get_run(run_id: str, _: None = Depends(https_required)):
    try:
        run = _get_run(run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        return RunDetails(**run)
    except HTTPException:
        raise
    except Exception as exc:
        raise as_http_exception(exc) from exc


@router.get("/artifacts/{run_id}")
def get_artifacts(run_id: str, _: None = Depends(https_required)):
    try:
        artifacts = _list_artifacts(run_id)
        return artifacts
    except Exception as exc:
        raise as_http_exception(exc) from exc


@router.get("/artifacts/{run_id}/file")
def get_artifact_file(run_id: str, path: str, _: None = Depends(https_required)):
    try:
        content = _get_artifact_content(run_id, path)
        if content is None:
            raise HTTPException(status_code=404, detail="Artifact not found")
        return {"path": path, "content": content}
    except HTTPException:
        raise
    except Exception as exc:
        raise as_http_exception(exc) from exc
