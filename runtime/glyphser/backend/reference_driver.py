"""Deterministic reference backend driver."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple


class ReferenceDriver:
    driver_id = "reference"
    backend_binary_hash = "sha256:reference"
    runtime_fingerprint_hash = "sha256:reference-runtime"

    def supports(self, instr: str, mode: str) -> bool:
        return instr in {
            "Input",
            "Dense",
            "Add",
            "Mul",
            "Relu",
            "Sigmoid",
            "Identity",
            "Output",
        }

    def dispatch(
        self,
        instr: str,
        inputs: List[Any],
        params: Dict[str, Any],
        theta: Dict[str, Any],
        mode: str,
        rng_state: int,
    ) -> Tuple[Any, int]:
        if instr == "Input":
            if not inputs:
                raise ValueError("Input node missing input data")
            return inputs[0], rng_state
        if instr == "Identity":
            return inputs[0], rng_state
        if instr == "Output":
            return inputs[0], rng_state
        if instr == "Add":
            a, b = inputs
            return [x + y for x, y in zip(a, b)], rng_state
        if instr == "Mul":
            a, b = inputs
            return [x * y for x, y in zip(a, b)], rng_state
        if instr == "Relu":
            a = inputs[0]
            return [x if x > 0 else 0 for x in a], rng_state
        if instr == "Sigmoid":
            import math

            a = inputs[0]
            return [1 / (1 + math.exp(-x)) for x in a], rng_state
        if instr == "Dense":
            x = inputs[0]
            weights = params.get("weights") or theta.get("weights") or []
            bias = params.get("bias") or theta.get("bias") or 0.0
            if not weights:
                raise ValueError("Dense weights missing")
            if isinstance(weights[0], list):
                out = []
                for row in weights:
                    out.append(sum(v * w for v, w in zip(x, row)))
            else:
                out = [sum(v * w for v, w in zip(x, weights))]
            if isinstance(bias, list):
                out = [o + b for o, b in zip(out, bias)]
            else:
                out = [o + bias for o in out]
            return out, rng_state
        raise ValueError(f"unsupported instr: {instr}")


def get_default_driver() -> ReferenceDriver:
    return ReferenceDriver()
