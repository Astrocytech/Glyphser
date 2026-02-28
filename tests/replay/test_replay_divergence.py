from __future__ import annotations

import pytest

from runtime.glyphser.model.model_ir_executor import execute


def _demo_ir():
    return {
        "ir_schema_hash": "sha256:uml_model_ir_demo",
        "nodes": [
            {"node_id": "input", "instr": "Input", "inputs": [], "shape_out": [4], "dtype": "float32"},
            {
                "node_id": "dense",
                "instr": "Dense",
                "inputs": [{"node_id": "input", "output_idx": 0}],
                "params": {"weights": [0.1, 0.2, 0.3, 0.4], "bias": 0.0},
                "shape_out": [1],
                "dtype": "float32",
            },
            {"node_id": "output", "instr": "Output", "inputs": [{"node_id": "dense", "output_idx": 0}], "shape_out": [1], "dtype": "float32"},
        ],
        "outputs": [{"node_id": "output", "output_idx": 0}],
    }


@pytest.mark.replay_scale
def test_replay_divergence_multi_rank_long_horizon():
    request = {
        "ir_dag": _demo_ir(),
        "input_data": {"input": [1.0, 2.0, 3.0, 4.0]},
        "mode": "forward",
        "replay_token": "replay-demo",
        "tmmu_context": {"arena_config": {"default": {"capacity_bytes": 1000000, "alignment_bytes": 64}}},
    }
    run_a = execute(request)
    run_b = execute(request)
    assert run_a["outputs"] == run_b["outputs"]
    assert run_a["execution_fp"] == run_b["execution_fp"]
