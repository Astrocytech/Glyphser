"""5-minute proof demo for Glyphser determinism.

Demonstrates:
1) Same seed => same digest
2) Different seed => different digest
"""

from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path

import cbor2

try:
    import numpy as np
    import torch
except Exception as exc:  # pragma: no cover - optional dependency
    raise SystemExit("This demo requires torch and numpy. Install with: python -m pip install torch numpy") from exc

from glyphser.internal.hashing import canonical_sha256

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence" / "demo"


@dataclass(frozen=True)
class DemoEvidence:
    seed: int
    final_loss: float
    weight: float
    bias: float


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)


def run_train(seed: int) -> DemoEvidence:
    set_seed(seed)
    x = torch.tensor([[0.0], [1.0], [2.0], [3.0]], dtype=torch.float32)
    y = torch.tensor([[1.0], [3.0], [5.0], [7.0]], dtype=torch.float32)

    model = torch.nn.Linear(1, 1)
    optim = torch.optim.SGD(model.parameters(), lr=0.05)
    loss_fn = torch.nn.MSELoss()

    loss = 0.0
    for _ in range(120):
        optim.zero_grad()
        pred = model(x)
        loss_tensor = loss_fn(pred, y)
        loss_tensor.backward()
        optim.step()
        loss = float(loss_tensor.item())

    return DemoEvidence(
        seed=seed,
        final_loss=loss,
        weight=float(model.weight.detach().cpu().numpy().flatten()[0]),
        bias=float(model.bias.detach().cpu().numpy().flatten()[0]),
    )


def write_manifest(name: str, payload: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest_json = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    (OUT / f"{name}.json").write_text(manifest_json, encoding="utf-8")
    (OUT / f"{name}.cbor").write_bytes(cbor2.dumps(payload))


def digest(ev: DemoEvidence) -> str:
    return canonical_sha256(asdict(ev))


def main() -> int:
    same_a = run_train(7)
    same_b = run_train(7)
    diff = run_train(99)

    d_same_a = digest(same_a)
    d_same_b = digest(same_b)
    d_diff = digest(diff)

    summary = {
        "same_seed_match": d_same_a == d_same_b,
        "different_seed_diverges": d_same_a != d_diff,
        "digest_same_a": d_same_a,
        "digest_same_b": d_same_b,
        "digest_diff": d_diff,
        "evidence_dir": str(OUT),
    }

    write_manifest("same_seed_run_a", asdict(same_a) | {"digest": d_same_a})
    write_manifest("same_seed_run_b", asdict(same_b) | {"digest": d_same_b})
    write_manifest("different_seed_run", asdict(diff) | {"digest": d_diff})
    write_manifest("summary", summary)

    print(json.dumps(summary, indent=2, sort_keys=True))
    if not summary["same_seed_match"] or not summary["different_seed_diverges"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
