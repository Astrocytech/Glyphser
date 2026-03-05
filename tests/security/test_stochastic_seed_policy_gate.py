from __future__ import annotations

import json
from pathlib import Path

from tooling.security import stochastic_seed_policy_gate


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(payload, str):
        path.write_text(payload, encoding="utf-8")
        return
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_stochastic_seed_policy_gate_passes_for_seeded_simulation_scripts(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "stochastic_seed_policy.json"
    _write(
        policy,
        {
            "require_seed_hashing": True,
            "stochastic_simulations": [
                {
                    "script": "tooling/security/sim_a.py",
                    "seed_env": "GLYPHSER_SIM_A_SEED",
                    "seed_summary_field": "sample_seed",
                }
            ],
        },
    )
    _write(
        repo / "tooling" / "security" / "sim_a.py",
        'import hashlib\nimport os\nimport random\nseed = os.environ.get("GLYPHSER_SIM_A_SEED", "fixed")\n'
        "rng = random.Random(int(hashlib.sha256(seed.encode()).hexdigest()[:8], 16))\n"
        'payload = {"summary": {"sample_seed": seed}}\n',
    )

    monkeypatch.setattr(stochastic_seed_policy_gate, "ROOT", repo)
    monkeypatch.setattr(stochastic_seed_policy_gate, "POLICY", policy)
    monkeypatch.setattr(stochastic_seed_policy_gate, "evidence_root", lambda: repo / "evidence")
    assert stochastic_seed_policy_gate.main([]) == 0


def test_stochastic_seed_policy_gate_fails_when_seed_binding_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "stochastic_seed_policy.json"
    _write(
        policy,
        {
            "require_seed_hashing": True,
            "stochastic_simulations": [
                {
                    "script": "tooling/security/sim_b.py",
                    "seed_env": "GLYPHSER_SIM_B_SEED",
                    "seed_summary_field": "sample_seed",
                }
            ],
        },
    )
    _write(
        repo / "tooling" / "security" / "sim_b.py",
        'import os\nimport random\nseed = os.environ.get("WRONG_SEED", "x")\nrng = random.Random(7)\npayload = {"summary": {}}\n',
    )

    monkeypatch.setattr(stochastic_seed_policy_gate, "ROOT", repo)
    monkeypatch.setattr(stochastic_seed_policy_gate, "POLICY", policy)
    monkeypatch.setattr(stochastic_seed_policy_gate, "evidence_root", lambda: repo / "evidence")
    assert stochastic_seed_policy_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "stochastic_seed_policy_gate.json").read_text(encoding="utf-8"))
    assert "missing_seed_env_binding:tooling/security/sim_b.py:GLYPHSER_SIM_B_SEED" in report["findings"]
    assert "missing_seed_summary_field:tooling/security/sim_b.py:sample_seed" in report["findings"]
    assert "missing_seed_hashing:tooling/security/sim_b.py" in report["findings"]
