"""Deterministic Keras/TensorFlow CPU backend driver."""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Tuple

try:
    import tensorflow as _tf
except Exception:  # pragma: no cover - exercised when tensorflow is unavailable
    _tf = None


def _hash_payload(payload: Dict[str, Any]) -> str:
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return f"sha256:{hashlib.sha256(text.encode('utf-8')).hexdigest()}"


def _to_tensor_cpu(value: Any) -> Any:
    if _tf is None:
        raise RuntimeError("tensorflow is not available")
    with _tf.device("/CPU:0"):
        return _tf.convert_to_tensor(value, dtype=_tf.float64)


def _to_python(value: Any) -> Any:
    if _tf is not None and isinstance(value, _tf.Tensor):
        return value.numpy().tolist()
    return value


class KerasCPUDriver:
    driver_id = "keras_cpu"

    def __init__(self) -> None:
        if _tf is None:
            raise RuntimeError("tensorflow is not available")
        _tf.random.set_seed(0)
        try:
            _tf.config.experimental.enable_op_determinism()
        except Exception:
            pass
        self.backend_binary_hash = _hash_payload(
            {
                "runtime": "tensorflow",
                "device": "cpu",
                "version": _tf.__version__,
            }
        )
        self.runtime_fingerprint_hash = _hash_payload(
            {
                "runtime": "tensorflow",
                "device": "cpu",
                "version": _tf.__version__,
                "deterministic_ops": True,
                "seed": 0,
            }
        )

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
        if _tf is None:
            raise RuntimeError("tensorflow is not available")

        if instr == "Input":
            if not inputs:
                raise ValueError("Input node missing input data")
            return _to_python(inputs[0]), rng_state
        if instr == "Identity":
            return _to_python(inputs[0]), rng_state
        if instr == "Output":
            return _to_python(inputs[0]), rng_state
        if instr == "Add":
            with _tf.device("/CPU:0"):
                a = _to_tensor_cpu(inputs[0])
                b = _to_tensor_cpu(inputs[1])
                return _to_python(a + b), rng_state
        if instr == "Mul":
            with _tf.device("/CPU:0"):
                a = _to_tensor_cpu(inputs[0])
                b = _to_tensor_cpu(inputs[1])
                return _to_python(a * b), rng_state
        if instr == "Relu":
            with _tf.device("/CPU:0"):
                a = _to_tensor_cpu(inputs[0])
                return _to_python(_tf.nn.relu(a)), rng_state
        if instr == "Sigmoid":
            with _tf.device("/CPU:0"):
                a = _to_tensor_cpu(inputs[0])
                return _to_python(_tf.math.sigmoid(a)), rng_state
        if instr == "Dense":
            with _tf.device("/CPU:0"):
                x = _to_tensor_cpu(inputs[0])
                weights = params.get("weights") or theta.get("weights") or []
                bias = params.get("bias") or theta.get("bias") or 0.0
                if not weights:
                    raise ValueError("Dense weights missing")
                w = _to_tensor_cpu(weights)
                if len(w.shape) == 1:
                    out = _tf.reshape(_tf.reduce_sum(x * w), [1])
                else:
                    out = _tf.linalg.matvec(w, x)
                b = _to_tensor_cpu(bias)
                out = out + b
                return _to_python(out), rng_state
        raise ValueError(f"unsupported instr: {instr}")


def get_keras_cpu_driver() -> KerasCPUDriver:
    return KerasCPUDriver()
