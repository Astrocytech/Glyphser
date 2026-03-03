# API Reference

This file is auto-generated from the stable `glyphser.public` API.

Regenerate with:
```bash
python tooling/docs/generate_api_reference.py
```

## `verify`

Type: `function`

Signature: `verify(model: 'dict[str, Any]', input_data: 'dict[str, Any] | None' = None) -> 'VerificationResult'`

Execute a model deterministically and return a verification digest.

Args:
    model: Model IR DAG dictionary.
    input_data: Optional model inputs.

## `VerificationResult`

Type: `dataclass`

Signature: `VerificationResult(digest: 'str', output: 'dict[str, Any]') -> None`

VerificationResult(digest: 'str', output: 'dict[str, Any]')

## `RuntimeApiConfig`

Type: `dataclass`

Signature: `RuntimeApiConfig(root: 'Path', state_path: 'Path', audit_log_path: 'Path | None' = None, api_version: 'str' = '1.0.0') -> None`

RuntimeApiConfig(root: 'Path', state_path: 'Path', audit_log_path: 'Path | None' = None, api_version: 'str' = '1.0.0')

## `RuntimeService`

Type: `class`

Signature: `RuntimeService(config: 'RuntimeApiConfig') -> 'None'`

Minimal deterministic API service with file-backed state.
