from __future__ import annotations

from glyphser import RuntimeApiConfig, RuntimeService, verify


def test_public_runtime_service_wrapper(tmp_path):
    svc = RuntimeService(RuntimeApiConfig(root=tmp_path, state_path=tmp_path / "state.json"))
    created = svc.submit_job(payload={"payload": {"x": 1}}, token="role:admin", scope="jobs:write")
    loaded = svc.status(created["job_id"], token="role:admin", scope="jobs:read")
    assert loaded["job_id"] == created["job_id"]


def test_verify_returns_digest():
    model = {
        "ir_hash": "unit-ir",
        "nodes": [
            {"node_id": "x", "instr": "Input", "shape_out": [1], "dtype": "f32"},
        ],
        "outputs": [{"node_id": "x", "output_idx": 0}],
    }
    result = verify(model, {"x": [1.0]})
    assert len(result.digest) == 64
    assert isinstance(result.output, dict)
