# API Stability Contract

## Stable Surface

Only modules under `glyphser.public` are considered stable API.

Stable entrypoints in `v0.1.x`:
- `glyphser.verify`
- `glyphser.VerificationResult`
- `glyphser.RuntimeApiConfig`
- `glyphser.RuntimeService`
- `glyphser.public.*`

## Internal Surface

The following are internal and may change without notice:
- `glyphser.internal.*`
- `runtime.glyphser.*`
- `tooling/*`

## Compatibility Rules

- Breaking public API changes require a major version bump.
- New additive public API can ship in minor releases.
- Internal refactors can ship in any release while preserving public contracts.
