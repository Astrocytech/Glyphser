from __future__ import annotations

from runtime.glyphser.tmmu.prepare_memory import prepare_memory


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


def test_tmmu_plan_deterministic():
    request = {
        "ir_dag": _demo_ir(),
        "mode": "forward",
        "replay_token": "demo",
        "tmmu_context": {"arena_config": {"default": {"capacity_bytes": 1000000, "alignment_bytes": 64}}},
    }
    a = prepare_memory(request)
    b = prepare_memory(request)
    assert a["tmmu_plan_hash"] == b["tmmu_plan_hash"]
    assert a["tensor_map"] == b["tensor_map"]
