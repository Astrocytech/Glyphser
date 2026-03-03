# Compatibility Matrix

| Dimension | Supported | Notes |
|---|---|---|
| Python | 3.12 | Primary supported runtime for `v0.1.x`. |
| OS | Linux, macOS, Windows | Core APIs are OS-agnostic; CI evidence is Linux-first today. |
| Backends | `default`, `pytorch`, `keras` | Determinism guarantees depend on backend and profile constraints. |
| Install Mode | `pip install glyphser`, editable install | Both are supported for development and CI. |

## Scope

This matrix applies to the stable API documented in `docs/API_STABILITY.md`.
