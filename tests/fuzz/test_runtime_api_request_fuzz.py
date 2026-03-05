from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

from runtime.glyphser.api.runtime_api import RuntimeApiConfig, RuntimeApiService, _validate_against_schema

ROOT = Path(__file__).resolve().parents[2]


def _mutate_json_text(rng: random.Random, raw: str) -> str:
    if not raw:
        return raw
    mode = rng.randrange(0, 5)
    if mode == 0:
        cut = rng.randrange(0, len(raw))
        return raw[:cut]
    if mode == 1:
        pos = rng.randrange(0, len(raw))
        return raw[:pos] + raw[pos + 1 :]
    if mode == 2:
        pos = rng.randrange(0, len(raw))
        return raw[:pos] + rng.choice(["}", "]", "{", "[", ":", ",", '"']) + raw[pos:]
    if mode == 3:
        return raw.replace('"payload"', rng.choice(['"payload "', '"paylo\\u0061d"', '"\\u0070ayload"']), 1)
    return raw.replace('"idempotency_key":""', '"idempotency_key":null', 1)


def test_runtime_api_submit_malformed_json_fuzz_never_crashes(tmp_path: Path) -> None:
    svc = RuntimeApiService(RuntimeApiConfig(root=ROOT, state_path=tmp_path / "state.json"))
    seed = {
        "payload": {"job": "demo", "v": 1},
        "token": "token-a",
        "scope": "jobs:write",
        "idempotency_key": "",
    }
    raw = json.dumps(seed, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    rng = random.Random(20260305)

    for _ in range(500):
        candidate = _mutate_json_text(rng, raw)
        try:
            parsed: Any = json.loads(candidate)
        except json.JSONDecodeError:
            continue

        if not isinstance(parsed, dict):
            continue
        payload = parsed.get("payload")
        token = parsed.get("token", "token-a")
        scope = parsed.get("scope", "jobs:write")
        idem = parsed.get("idempotency_key", "")
        if idem is None:
            idem = ""

        try:
            svc.submit_job(payload=payload, token=token, scope=scope, idempotency_key=idem)
        except (TypeError, ValueError):
            pass


def test_runtime_api_submit_schema_bypass_fuzz_rejected() -> None:
    rng = random.Random(20260306)
    base = {
        "payload": {"ok": True},
        "token": "token-a",
        "scope": "jobs:write",
        "idempotency_key": "",
    }
    bypass_keys = [
        "payload ",
        " payload",
        "pay\u200bload",
        "\ufeffpayload",
        "__proto__",
        "constructor",
        "token\n",
        "scope\t",
    ]

    for _ in range(250):
        case = dict(base)
        attack_key = rng.choice(bypass_keys)
        case[attack_key] = {"x": 1}
        if rng.random() < 0.5:
            case.pop("payload", None)
        try:
            _validate_against_schema("submit_request", case)
            assert False, f"schema bypass accepted unexpectedly: {attack_key!r}"
        except ValueError:
            pass


def test_runtime_api_submit_boundary_fuzz_for_sizes_and_limits(tmp_path: Path) -> None:
    svc = RuntimeApiService(
        RuntimeApiConfig(
            root=ROOT,
            state_path=tmp_path / "state.json",
            submit_payload_max_bytes=64,
            submit_payload_max_depth=3,
            submit_payload_max_items=16,
        )
    )

    payloads = [
        {"payload": {"msg": "x" * 1}},
        {"payload": {"msg": "x" * 48}},
        {"payload": {"msg": "x" * 1024}},
        {"payload": {"a": {"b": {"c": 1}}}},
        {"payload": {"a": {"b": {"c": {"d": 1}}}}},
        {"payload": {f"k{ix}": ix for ix in range(4)}},
        {"payload": {f"k{ix}": ix for ix in range(64)}},
    ]
    token_sizes = [8, 128, 4096, 4097]
    idempotency_sizes = [0, 1, 64, 128, 129]

    for payload in payloads:
        for tlen in token_sizes:
            for ilen in idempotency_sizes:
                token = "a" * tlen
                idempotency_key = "k" * ilen
                try:
                    svc.submit_job(
                        payload=payload,
                        token=token,
                        scope="jobs:write",
                        idempotency_key=idempotency_key,
                    )
                except ValueError:
                    pass
