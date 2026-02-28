# API Lifecycle and Deprecation Policy (Milestone 18)

## SemVer Rules
- MAJOR: breaking API schema or behavior change.
- MINOR: backward-compatible additions.
- PATCH: backward-compatible fixes.

## Support Window
- Minimum support window for a major API line: 12 months.
- Deprecation window: at least 2 release cycles before removal.

## Deprecation Signaling
- Release notes must list deprecated endpoints/fields with removal target.
- API docs must mark deprecated fields/endpoints explicitly.

## Compatibility Testing Policy
- Contract tests must pass for all non-deprecated endpoints.
- Changes classified as breaking must either:
- move to next major API version, or
- be rejected by contract gate.

Canonical source references: `specs/` and `specs/schemas/` define normative behavior for this document.
