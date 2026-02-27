from __future__ import annotations

import os
import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "chaos: requires distributed chaos harness")
    config.addinivalue_line("markers", "replay_scale: requires multi-rank replay harness")
    config.addinivalue_line("markers", "fuzz_harness: requires external fuzz harness")
    config.addinivalue_line("markers", "regression_matrix: requires GPU/driver matrix")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    enable_chaos = os.getenv("GLYPHSER_ENABLE_CHAOS") == "1"
    enable_replay_scale = os.getenv("GLYPHSER_ENABLE_REPLAY_SCALE") == "1"
    enable_fuzz = os.getenv("GLYPHSER_ENABLE_FUZZ_HARNESS") == "1"
    enable_matrix = os.getenv("GLYPHSER_ENABLE_REGRESSION_MATRIX") == "1"

    for item in items:
        if "chaos" in item.keywords and not enable_chaos:
            item.add_marker(pytest.mark.skip(reason="Set GLYPHSER_ENABLE_CHAOS=1 to run chaos tests."))
        if "replay_scale" in item.keywords and not enable_replay_scale:
            item.add_marker(pytest.mark.skip(reason="Set GLYPHSER_ENABLE_REPLAY_SCALE=1 to run replay scale tests."))
        if "fuzz_harness" in item.keywords and not enable_fuzz:
            item.add_marker(pytest.mark.skip(reason="Set GLYPHSER_ENABLE_FUZZ_HARNESS=1 to run fuzz harness tests."))
        if "regression_matrix" in item.keywords and not enable_matrix:
            item.add_marker(pytest.mark.skip(reason="Set GLYPHSER_ENABLE_REGRESSION_MATRIX=1 to run regression matrix tests."))
