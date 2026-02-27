from __future__ import annotations

import pytest

from src.glyphser.data_structures.validate_struct import (
    validate_checkpoint_header,
    validate_trace_iter_record,
)


def test_validate_trace_iter_record_accepts_valid():
    validate_trace_iter_record({"t": 0, "operator_id": "Glyphser.Data.NextBatch"})


def test_validate_trace_iter_record_rejects_non_dict():
    with pytest.raises(TypeError):
        validate_trace_iter_record([])


def test_validate_trace_iter_record_rejects_missing_fields():
    with pytest.raises(ValueError):
        validate_trace_iter_record({"t": 0})


def test_validate_checkpoint_header_accepts_valid():
    validate_checkpoint_header({"checkpoint_id": "chk0", "step": 0})


def test_validate_checkpoint_header_rejects_non_dict():
    with pytest.raises(TypeError):
        validate_checkpoint_header("bad")


def test_validate_checkpoint_header_rejects_missing_fields():
    with pytest.raises(ValueError):
        validate_checkpoint_header({"step": 0})
