from __future__ import annotations

import pytest


def _simulate_rank_events(world_size: int) -> list[dict]:
    return [{"rank": rank, "event": "heartbeat", "step": 1} for rank in range(world_size)]


def _detect_missing_ranks(events: list[dict], world_size: int) -> list[int]:
    seen = {e["rank"] for e in events}
    return [r for r in range(world_size) if r not in seen]


@pytest.mark.chaos
def test_distributed_chaos_rank_loss():
    world_size = 4
    events = _simulate_rank_events(world_size)
    # simulate rank loss
    events = [e for e in events if e["rank"] != 2]
    missing = _detect_missing_ranks(events, world_size)
    assert missing == [2]


@pytest.mark.chaos
def test_distributed_chaos_network_partition():
    world_size = 4
    events = _simulate_rank_events(world_size)
    # simulate partition: ranks 0,1 isolated from 2,3
    partition_a = [e for e in events if e["rank"] in (0, 1)]
    partition_b = [e for e in events if e["rank"] in (2, 3)]
    assert {e["rank"] for e in partition_a} == {0, 1}
    assert {e["rank"] for e in partition_b} == {2, 3}


@pytest.mark.chaos
def test_distributed_chaos_delayed_collective():
    events = [
        {"rank": 0, "event": "collective", "t": 1},
        {"rank": 1, "event": "collective", "t": 1},
        {"rank": 2, "event": "collective", "t": 5},  # delayed
    ]
    ordered = sorted(events, key=lambda e: (e["t"], e["rank"]))
    assert ordered[0]["t"] == 1
    assert ordered[-1]["t"] == 5
