"""Deterministic ModelIR executor implementation."""
from __future__ import annotations

from typing import Any, Dict, List

from runtime.glyphser.backend.load_driver import resolve_driver
from runtime.glyphser.contract.validate import ContractViolationError, validate_contract
from runtime.glyphser.error.emit import emit_error
from runtime.glyphser.fingerprint.state_fingerprint import state_fingerprint
from runtime.glyphser.model.build_grad_dependency_order import build_grad_dependency_order
from runtime.glyphser.model.collect_gradients import collect_gradients
from runtime.glyphser.model.dispatch_primitive import PrimitiveUnsupportedError, ShapeMismatchError, dispatch_primitive
from runtime.glyphser.model.topo_sort_nodes import topo_sort_nodes
from runtime.glyphser.tmmu.commit_execution import commit_execution
from runtime.glyphser.tmmu.prepare_memory import prepare_memory


def _resolve_input_data(input_data: Any) -> Dict[str, Any]:
    if input_data is None:
        return {}
    if isinstance(input_data, dict):
        return input_data
    raise ValueError("input_data must be dict")


def _extract_inputs(node: Dict[str, Any], tensor_map: Dict[str, Dict[str, Any]], input_data: Dict[str, Any]) -> List[Any]:
    if node["instr"] == "Input":
        return [input_data.get(node["node_id"])]
    values: List[Any] = []
    for ref in node.get("inputs", []):
        if "node_id" in ref:
            tensor_id = f"{ref['node_id']}:{ref.get('output_idx', 0)}"
            if tensor_id not in tensor_map:
                raise ValueError(f"missing tensor: {tensor_id}")
            values.append(tensor_map[tensor_id]["value"])
        elif "input_key" in ref:
            values.append(input_data.get(ref["input_key"]))
    return values


def execute(request: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(request, dict):
        return {"error": emit_error("CONTRACT_VIOLATION", "invalid request", operator_id="Glyphser.Model.ModelIR_Executor")}

    ir_dag = request.get("ir_dag") or request.get("uml_model_ir_dag")
    if ir_dag is None:
        return {"error": emit_error("INVALID_IR", "ir_dag missing", operator_id="Glyphser.Model.ModelIR_Executor", ir_hash="", node_id="")}

    mode = request.get("mode", "forward")
    replay_token = request.get("replay_token") or ""
    theta = request.get("theta", {})
    input_data = _resolve_input_data(request.get("input_data") or request.get("batch"))
    rng_state = int(request.get("rng_state", 0))
    tmmu_context = request.get("tmmu_context", {})

    driver = request.get("driver")
    if driver is None:
        driver_id = request.get("driver_id") or "default"
        try:
            driver = resolve_driver(driver_id, request=request)
        except Exception:
            return {
                "error": emit_error(
                    "PRIMITIVE_UNSUPPORTED",
                    "unsupported primitive",
                    operator_id="Glyphser.Model.ModelIR_Executor",
                    t="",
                    node_id="",
                    instr="",
                    backend_binary_hash="",
                )
            }

    try:
        ir = validate_contract(ir_dag, driver, mode)
    except ContractViolationError:
        return {"error": emit_error("PRIMITIVE_UNSUPPORTED", "unsupported primitive", operator_id="Glyphser.Model.ModelIR_Executor", t="", node_id="", instr="", backend_binary_hash=getattr(driver, "backend_binary_hash", ""))}
    except Exception:
        return {"error": emit_error("INVALID_IR", "invalid request", operator_id="Glyphser.Model.ModelIR_Executor", t="", ir_hash="", node_id="")}

    try:
        execution_order = topo_sort_nodes(ir["nodes"])
    except Exception:
        return {"error": emit_error("CYCLE_DETECTED", "invalid request", operator_id="Glyphser.Model.ModelIR_Executor", t="", ir_hash=ir.get("ir_hash", ""), node_id="")}

    if mode == "backward":
        try:
            backward_order, reverse_equivalent_flag = build_grad_dependency_order(ir, execution_order)
            if reverse_equivalent_flag:
                execution_order = list(reversed(execution_order))
            else:
                execution_order = backward_order
        except Exception:
            return {"error": emit_error("CYCLE_DETECTED", "invalid request", operator_id="Glyphser.Model.ModelIR_Executor", t="", ir_hash=ir.get("ir_hash", ""), node_id="")}

    try:
        tmmu_result = prepare_memory(
            {
                "ir_dag": ir,
                "execution_order": execution_order,
                "mode": mode,
                "replay_token": replay_token,
                "tmmu_context": tmmu_context,
            }
        )
    except Exception:
        return {"error": emit_error("TMMU_ALLOCATION_FAILURE", "invalid request", operator_id="Glyphser.Model.ModelIR_Executor", t="", arena="", peak_required_bytes="")}

    tensor_map = tmmu_result["tensor_map"]

    try:
        for node in execution_order:
            inputs = _extract_inputs(node, tensor_map, input_data)
            output, rng_state = dispatch_primitive(node, inputs, theta, mode, driver, rng_state)
            tensor_id = f"{node['node_id']}:0"
            if tensor_id in tensor_map:
                tensor_map[tensor_id]["value"] = output
            else:
                tensor_map[tensor_id] = {"value": output, "shape": node.get("shape_out"), "dtype": node.get("dtype")}
    except ShapeMismatchError:
        return {"error": emit_error("SHAPE_MISMATCH", "invalid request", operator_id="Glyphser.Model.ModelIR_Executor", t="", node_id="", shape_in="", shape_expected="")}
    except PrimitiveUnsupportedError:
        return {"error": emit_error("PRIMITIVE_UNSUPPORTED", "invalid request", operator_id="Glyphser.Model.ModelIR_Executor", t="", node_id="", instr="", backend_binary_hash=getattr(driver, "backend_binary_hash", ""))}
    except Exception:
        return {"error": emit_error("CONTRACT_VIOLATION", "invalid request", operator_id="Glyphser.Model.ModelIR_Executor", t="", replay_token="", failure_operator="")}

    outputs = []
    for out in ir.get("outputs", []):
        tensor_id = f"{out['node_id']}:{out.get('output_idx', 0)}"
        outputs.append(tensor_map[tensor_id]["value"])

    grads = collect_gradients(tensor_map, ir) if mode == "backward" else None
    tmmu_state_next = commit_execution(tmmu_result.get("tmmu_state_next", {}))

    execution_fp = state_fingerprint(
        {
            "ir_hash": ir.get("ir_hash"),
            "mode": mode,
            "outputs": outputs,
            "tmmu_plan_hash": tmmu_result.get("tmmu_plan_hash"),
            "rng_state": rng_state,
        }
    )

    response: Dict[str, Any] = {
        "outputs": outputs,
        "execution_fp": execution_fp,
        "tmmu_state_next": tmmu_state_next,
        "rng_state_next": rng_state,
    }
    if grads is not None:
        response["grads"] = grads
    return response
