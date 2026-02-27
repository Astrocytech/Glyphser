"""Deterministic forward wrapper."""
from __future__ import annotations

from typing import Any, Dict

from src.glyphser.error.emit import emit_error
from src.glyphser.model.model_ir_executor import execute


def forward(request: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(request, dict):
        return {"error": emit_error("CONTRACT_VIOLATION", "invalid request", operator_id="Glyphser.Model.Forward")}
    ir_dag = request.get("ir_dag") or request.get("uml_model_ir_dag")
    if ir_dag is None:
        return {"error": emit_error("CONTRACT_VIOLATION", "invalid request", operator_id="Glyphser.Model.Forward")}
    executor_request = {
        "ir_dag": ir_dag,
        "theta": request.get("theta", {}),
        "input_data": request.get("input_data") or request.get("batch") or {},
        "mode": "forward",
        "replay_token": request.get("replay_token") or "",
        "tmmu_context": request.get("tmmu_context", {}),
        "rng_state": request.get("rng_state", 0),
    }
    return execute(executor_request)
