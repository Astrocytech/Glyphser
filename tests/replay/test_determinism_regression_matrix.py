from __future__ import annotations

import pytest

from runtime.glyphser.model.model_ir_executor import execute


def _demo_ir():
    return {
        "ir_schema_hash": "sha256:uml_model_ir_demo",
        "nodes": [
            {
                "node_id": "input",
                "instr": "Input",
                "inputs": [],
                "shape_out": [4],
                "dtype": "float32",
            },
            {
                "node_id": "dense",
                "instr": "Dense",
                "inputs": [{"node_id": "input", "output_idx": 0}],
                "params": {"weights": [0.1, 0.2, 0.3, 0.4], "bias": 0.0},
                "shape_out": [1],
                "dtype": "float32",
            },
            {
                "node_id": "output",
                "instr": "Output",
                "inputs": [{"node_id": "dense", "output_idx": 0}],
                "shape_out": [1],
                "dtype": "float32",
            },
        ],
        "outputs": [{"node_id": "output", "output_idx": 0}],
    }


def _run(reference_token: str) -> dict:
    return execute(
        {
            "ir_dag": _demo_ir(),
            "input_data": {"input": [1.0, 2.0, 3.0, 4.0]},
            "mode": "forward",
            "replay_token": reference_token,
            "tmmu_context": {"arena_config": {"default": {"capacity_bytes": 1000000, "alignment_bytes": 64}}},
        }
    )


@pytest.mark.regression_matrix
def test_regression_matrix_same_machine_e0():
    a = _run("matrix-e0")
    b = _run("matrix-e0")
    assert a["outputs"] == b["outputs"]
    assert a["execution_fp"] == b["execution_fp"]


@pytest.mark.regression_matrix
def test_regression_matrix_same_gpu_class_e1():
    a = _run("matrix-e1")
    b = _run("matrix-e1")
    assert a["outputs"] == b["outputs"]


@pytest.mark.regression_matrix
def test_regression_matrix_cross_gpu_class_e1():
    a = _run("matrix-cross")
    b = _run("matrix-cross")
    assert a["outputs"] == b["outputs"]
