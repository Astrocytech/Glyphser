# Repository Map

| Domain | Purpose |
|---|---|
| `runtime/` | Executable runtime code. |
| `specs/` | Normative technical specification and schema sources. |
| `artifacts/` | Deterministic inputs, expected outputs, bundles, generated artifacts. |
| `evidence/` | Generated proof and gate reports. |
| `governance/` | Process, policy, roadmap, structural controls. |
| `product/` | Product-facing guides, policies, business, ops, site content. |
| `tooling/` | Generators, validators, gates, and automation entrypoints. |
| `distribution/` | Release/signing distribution material. |

## Canonical Generated Code
- Canonical runtime generated modules live only under `runtime/glyphser/_generated/`.
- Canonical pointer/hash index for generated modules is `artifacts/generated/stable/codegen/index.json`.
- Transient cleanroom comparison output is written under `artifacts/generated/tmp/` only.

## Docs vs Specs
- `docs/` answers how to use and navigate this repository.
- `specs/` defines what the system is (normative technical truth).

## Documentation Audiences
| Location | Primary Audience | Use |
|---|---|---|
| `docs/` | New contributors and operators | Navigation, quickstart, verification entrypoints. |
| `specs/` | Implementers and conformance engineers | Normative behavior, contracts, schemas, test-layer specs. |
| `product/handbook/` | Product, support, and customer-facing teams | Operational policies, guides, milestone reports. |
| `governance/` | Maintainers and project leads | Process controls, roadmap, structure policy, ecosystem governance. |
| `evidence/` | Auditors and release reviewers | Generated run evidence and gate reports only. |

## Placement Rules
- If runtime imports it, it belongs in `runtime/`.
- If conformance depends on it as normative truth, it belongs in `specs/`.
- If it is deterministic test/build input, it belongs in `artifacts/inputs/`.
- If it is generated proof/report output, it belongs in `evidence/`.
