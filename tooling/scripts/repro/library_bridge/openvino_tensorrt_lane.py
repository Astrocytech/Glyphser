#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from typing import Any


def _parse_csv(text: str) -> list[float]:
    if not text.strip():
        return []
    return [float(x.strip()) for x in text.split(",")]


def _detect_runtime() -> tuple[str, str]:
    try:
        import openvino  # type: ignore

        return "openvino_cpu", getattr(openvino, "__version__", "unknown")
    except Exception:
        pass
    try:
        import tensorrt  # type: ignore

        return "tensorrt", getattr(tensorrt, "__version__", "unknown")
    except Exception:
        pass
    raise RuntimeError("Neither OpenVINO nor TensorRT python package is available.")


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print(
            "usage: openvino_tensorrt_lane.py <input_csv> <weights_csv> <bias>",
            file=sys.stderr,
        )
        return 2
    runtime, version = _detect_runtime()
    inputs = _parse_csv(argv[1])
    weights = _parse_csv(argv[2])
    bias = float(argv[3])
    if len(inputs) != len(weights):
        print("input and weights length mismatch", file=sys.stderr)
        return 3
    out = sum(x * w for x, w in zip(inputs, weights)) + bias
    payload: dict[str, Any] = {
        "runtime": runtime,
        "runtime_version": version,
        "outputs": [[out]],
    }
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
