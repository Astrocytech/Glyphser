# Compatibility Matrix

| Dimension | Supported in `v0.1.x` | Notes |
|---|---|---|
| Python | 3.12 | Primary supported runtime. |
| OS | Linux, macOS, Windows | Core APIs are OS-agnostic; CI evidence is Linux-first today. |
| Backends | `default`, `pytorch`, `keras` | Determinism guarantees depend on backend and profile constraints. |
| Install Mode | `pip install glyphser`, editable install | Both are supported for development and CI. |

## Scope

This matrix applies to the stable API documented in `docs/API_STABILITY.md`.

## Upgrade guarantees

- Patch upgrades (`0.1.x -> 0.1.y`) are API compatible.
- Minor upgrades (`0.1.x -> 0.2.0`) remain backward-compatible unless a major bump is announced.
- Breaking public API changes require a major version (`1.0.0+`).
