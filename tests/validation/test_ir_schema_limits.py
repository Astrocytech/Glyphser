from __future__ import annotations

import pytest

from runtime.glyphser.model.ir_schema import IRValidationError, validate_ir_dag


def _minimal_ir() -> dict:
    return {
        "ir_schema_hash": "sha256:uml_model_ir_demo",
        "nodes": [
            {
                "node_id": "n0",
                "instr": "Input",
                "inputs": [],
                "shape_out": [1],
                "dtype": "float32",
            }
        ],
        "outputs": [{"node_id": "n0", "output_idx": 0}],
    }


def test_rejects_excessive_shape_rank() -> None:
    ir = _minimal_ir()
    ir["nodes"][0]["shape_out"] = [1] * 17
    with pytest.raises(IRValidationError, match="shape rank too large"):
        validate_ir_dag(ir)


def test_rejects_excessive_node_count() -> None:
    ir = {
        "ir_schema_hash": "sha256:uml_model_ir_demo",
        "nodes": [
            {
                "node_id": f"n{i}",
                "instr": "Input",
                "inputs": [],
                "shape_out": [1],
                "dtype": "float32",
            }
            for i in range(4097)
        ],
        "outputs": [{"node_id": "n0", "output_idx": 0}],
    }
    with pytest.raises(IRValidationError, match="too many nodes"):
        validate_ir_dag(ir)


def test_rejects_excessive_tensor_size() -> None:
    ir = _minimal_ir()
    ir["nodes"][0]["shape_out"] = [1_000_000, 600]
    with pytest.raises(IRValidationError, match="tensor size exceeds limit"):
        validate_ir_dag(ir)
