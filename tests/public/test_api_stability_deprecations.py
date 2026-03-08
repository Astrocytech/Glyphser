from __future__ import annotations

import warnings

import glyphser


def test_deprecated_runtime_api_service_alias_warns_and_resolves():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", DeprecationWarning)
        cls = glyphser.RuntimeApiService
    assert cls is glyphser.RuntimeService
    assert any("deprecated" in str(w.message).lower() for w in caught)


def test_deprecated_verify_model_alias_warns_and_resolves():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", DeprecationWarning)
        fn = glyphser.verify_model
    assert fn is glyphser.verify
    assert any("deprecated" in str(w.message).lower() for w in caught)
