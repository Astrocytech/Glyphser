# Versioning Policy

This project follows [Semantic Versioning 2.0.0](https://semver.org/).

## Public API scope

Only modules under `glyphser.public` (and top-level re-exports from `glyphser`) are versioned as stable API.

## Version semantics

- **MAJOR (`X.0.0`)**: breaking changes to stable public API.
- **MINOR (`x.Y.0`)**: backward-compatible new functionality.
- **PATCH (`x.y.Z`)**: bug fixes and documentation changes with no API breaks.

## Compatibility guarantees

- No breaking change to stable API within a minor line (`0.2.x`).
- Deprecated public symbols remain available for at least one minor release.
- Internal modules (`glyphser.internal.*`, `runtime.glyphser.*`) can change without notice.

## Current Status
Current Version: **0.2.0** (Public CLI and release hardening improvements)
