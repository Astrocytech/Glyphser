"""Minimal MLflow integration example for Glyphser digest/evidence logging."""

from __future__ import annotations

import json
from pathlib import Path

try:
    import mlflow
except Exception as exc:  # pragma: no cover - optional dependency
    raise SystemExit("Install requirements: python -m pip install mlflow") from exc

from glyphser import verify


MODEL = {
    "ir_hash": "mlflow-demo-ir",
    "nodes": [{"node_id": "x", "instr": "Input", "shape_out": [1], "dtype": "f32"}],
    "outputs": [{"node_id": "x", "output_idx": 0}],
}
INPUT = {"x": [1.0]}


def main() -> int:
    result = verify(MODEL, INPUT)
    evidence_path = Path("evidence/mlflow/verification.json")
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(
        json.dumps({"digest": result.digest, "output": result.output}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    with mlflow.start_run(run_name="glyphser_verification"):
        mlflow.log_param("glyphser_digest", result.digest)
        mlflow.log_param("glyphser_evidence_path", str(evidence_path))
        mlflow.log_artifact(str(evidence_path))

    print(f"Logged digest={result.digest} to MLflow")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
