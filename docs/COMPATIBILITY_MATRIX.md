# Compatibility Matrix

| Dimension | Supported in `v0.1.x` | Notes |
|---|---|---|
| Python | 3.11, 3.12 | Both versions are validated in CI matrix. |
| OS | Linux, macOS | Validated in CI matrix. |
| Backends | `default`, `pytorch`, `keras` | Determinism guarantees depend on backend and profile constraints. |
| Install Mode | `pip install glyphser`, editable install | Both are supported for development and CI. |

## Scope

This matrix applies to the stable API documented in `docs/STABILITY_CONTRACT.md`.

## Upgrade guarantees

- Patch upgrades (`0.1.x -> 0.1.y`) are API compatible.
- Minor upgrades (`0.1.x -> 0.2.0`) remain backward-compatible unless a major bump is announced.
- Breaking public API changes require a major version (`1.0.0+`).
