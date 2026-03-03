"""PyTorch deterministic integration example for Glyphser.

Flow:
1. Train a tiny model with fixed seeds.
2. Build a compact evidence payload from model state.
3. Hash evidence with Glyphser internal canonical hashing.
4. Re-run and verify digest parity.
"""

from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass

try:
    import numpy as np
    import torch
except Exception as exc:  # pragma: no cover - optional dependency
    raise SystemExit(
        "This example requires PyTorch and NumPy. "
        "Install with: python -m pip install torch numpy"
    ) from exc

from glyphser.internal.hashing import canonical_sha256


@dataclass(frozen=True)
class TrainingEvidence:
    seed: int
    epochs: int
    lr: float
    final_loss: float
    weight: float
    bias: float


def set_deterministic(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)


def train_once(seed: int = 7, epochs: int = 120, lr: float = 0.05) -> TrainingEvidence:
    set_deterministic(seed)

    x = torch.tensor([[0.0], [1.0], [2.0], [3.0]], dtype=torch.float32)
    y = torch.tensor([[1.0], [3.0], [5.0], [7.0]], dtype=torch.float32)

    model = torch.nn.Linear(1, 1)
    optim = torch.optim.SGD(model.parameters(), lr=lr)
    loss_fn = torch.nn.MSELoss()

    final_loss = 0.0
    for _ in range(epochs):
        optim.zero_grad()
        pred = model(x)
        loss = loss_fn(pred, y)
        loss.backward()
        optim.step()
        final_loss = float(loss.item())

    weight = float(model.weight.detach().cpu().numpy().flatten()[0])
    bias = float(model.bias.detach().cpu().numpy().flatten()[0])

    return TrainingEvidence(
        seed=seed,
        epochs=epochs,
        lr=lr,
        final_loss=final_loss,
        weight=weight,
        bias=bias,
    )


def digest_from_evidence(evidence: TrainingEvidence) -> str:
    return canonical_sha256(asdict(evidence))


def main() -> int:
    run_a = train_once()
    run_b = train_once()

    digest_a = digest_from_evidence(run_a)
    digest_b = digest_from_evidence(run_b)

    payload = {
        "run_a": asdict(run_a),
        "run_b": asdict(run_b),
        "digest_a": digest_a,
        "digest_b": digest_b,
        "match": digest_a == digest_b,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))

    if digest_a != digest_b:
        print("Digest mismatch: determinism check failed.")
        return 1
    print("Digest match: determinism check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
