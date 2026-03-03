# Deprecation Policy

## Policy

- Public API deprecations are announced in release notes and `CHANGELOG.md`.
- Deprecated public symbols remain available for at least one minor release before removal.
- Removal of a public symbol is a breaking change and requires a major version bump.

## Process

1. Mark symbol as deprecated in docs.
2. Add migration path in release notes.
3. Keep compatibility window through the next minor release.
4. Remove in a major release.

## Current Deprecated Aliases

- `glyphser.RuntimeApiService` -> use `glyphser.RuntimeService`
- `glyphser.verify_model` -> use `glyphser.verify`
