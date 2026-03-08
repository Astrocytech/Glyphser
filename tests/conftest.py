from __future__ import annotations

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "chaos: requires distributed chaos harness")
    config.addinivalue_line("markers", "replay_scale: requires multi-rank replay harness")
    config.addinivalue_line("markers", "fuzz_harness: requires external fuzz harness")
    config.addinivalue_line("markers", "regression_matrix: requires GPU/driver matrix")
