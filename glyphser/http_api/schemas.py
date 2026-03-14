from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

try:  # pydantic v2
    from pydantic import model_validator
except Exception:  # pragma: no cover - pydantic v1 fallback
    model_validator = None  # type: ignore[assignment]


class StatusResponse(BaseModel):
    message: str


class VerifyRequest(BaseModel):
    target: str | None = Field(default=None, description="Named fixture target (for example: hello-core).")
    model: dict[str, Any] | None = Field(default=None, description="Model IR DAG as a JSON object.")
    input_data: dict[str, Any] | None = Field(default=None, description="Optional model inputs.")

    if model_validator is not None:

        @model_validator(mode="after")  # type: ignore[misc]
        def _validate_target_or_model(self) -> "VerifyRequest":
            if bool(self.target) == bool(self.model):
                raise ValueError("provide exactly one of: target, model")
            return self
    else:

        def __init__(self, **data: Any):
            super().__init__(**data)
            if bool(getattr(self, "target", None)) == bool(getattr(self, "model", None)):
                raise ValueError("provide exactly one of: target, model")


class VerifyResponse(BaseModel):
    status: str = "PASS"
    digest: str
    output: dict[str, Any]


class VerifyFixtureResponse(BaseModel):
    status: str
    fixture: str
    evidence_dir: str | None = None
    expected: dict[str, Any] | None = None
    actual: dict[str, Any] | None = None
    evidence_files: list[str] | None = None


class SnapshotRequest(BaseModel):
    model: dict[str, Any]
    input_data: dict[str, Any] | None = None


class SnapshotResponse(BaseModel):
    status: str = "PASS"
    digest: str
    snapshot: dict[str, Any]


class SnapshotWriteRequest(BaseModel):
    model: dict[str, Any]
    input_data: dict[str, Any] | None = None
    name: str = Field(..., description="Snapshot filename (no path separators).")


class SnapshotWriteResponse(BaseModel):
    status: str = "PASS"
    digest: str
    path: str


class RuntimeSubmitRequest(BaseModel):
    payload: dict[str, Any]
    token: str
    scope: str
    idempotency_key: str | None = None


class RuntimeJobRequest(BaseModel):
    job_id: str
    token: str
    scope: str


class DoctorRequest(BaseModel):
    run_id: str | None = Field(default=None, description="Optional run id for workspace folder naming.")


class SetupRequest(BaseModel):
    profile: str = Field(..., description="available_local / available_local_partial / strict_universal")
    doctor_run_id: str | None = None
    doctor_manifest: dict[str, Any] | None = None
    dry_run: bool = False
    offline: bool = False
    max_retries: int = 1
    timeout_sec: int = 300
    run_id: str | None = None


class RouteRunRequest(BaseModel):
    profile: str = Field(default="auto", description="auto or profile label")
    doctor_run_id: str | None = None
    doctor_manifest: dict[str, Any] | None = None
    run_id: str | None = None


class CertifyRequest(BaseModel):
    profile: str
    run_id: str | None = None


class ApiSignatureValidateRequest(BaseModel):
    record: dict[str, Any]
    allowed_ops: list[Any] | None = None


class ApiSignatureValidateResponse(BaseModel):
    status: str = "PASS"


class ErrorClassifyRequest(BaseModel):
    message: str


class ErrorClassifyResponse(BaseModel):
    code: str


class ExplorerListResponse(BaseModel):
    root: str
    path: str
    entries: list[dict[str, Any]]


class ExplorerReadResponse(BaseModel):
    root: str
    path: str
    content: str


class IrValidateRequest(BaseModel):
    ir_dag: dict[str, Any]


class TraceHashRequest(BaseModel):
    records: list[dict[str, Any]]


class TraceHashResponse(BaseModel):
    trace_final_hash: str


class LoadDriverRequest(BaseModel):
    request: dict[str, Any]


class ContractValidateRequest(BaseModel):
    ir_dag: dict[str, Any]
    driver_request: dict[str, Any] = Field(default_factory=lambda: {"driver_id": "default"})
    mode: str = "forward"


class EvidenceValidateRequest(BaseModel):
    request: dict[str, Any]


class GenericOpRequest(BaseModel):
    request: dict[str, Any]


class CheckpointSaveRequest(BaseModel):
    state: dict[str, Any]
    name: str = Field(..., description="Checkpoint filename (no path separators).")


class CheckpointRestoreRequest(BaseModel):
    path: str = Field(..., description="Relative path under workspace root.")


class TraceWriteRequest(BaseModel):
    records: list[dict[str, Any]]
    name: str = Field(..., description="Trace filename (no path separators).")


class CertificateWriteRequest(BaseModel):
    evidence: dict[str, Any]
    name: str = Field(..., description="Certificate filename (no path separators).")


class NextBatchRequest(BaseModel):
    dataset: list[Any]
    cursor: int
    batch_size: int


class InterfaceHashRequest(BaseModel):
    registry: dict[str, Any]
