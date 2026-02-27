"""Contract validation for IR and driver compatibility."""
from __future__ import annotations

from typing import Any, Dict

from src.glyphser.model.ir_schema import validate_ir_dag


class ContractViolationError(RuntimeError):
    pass


def validate_contract(ir_dag: Dict[str, Any], driver: Any, mode: str) -> Dict[str, Any]:
    normalized = validate_ir_dag(ir_dag)
    for node in normalized["nodes"]:
        instr = node["instr"]
        if not driver.supports(instr, mode):
            raise ContractViolationError(f"unsupported instr: {instr}")
    return normalized
