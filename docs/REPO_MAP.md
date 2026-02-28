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

## Placement Rules
- If runtime imports it, it belongs in `runtime/`.
- If conformance depends on it as normative truth, it belongs in `specs/`.
- If it is deterministic test/build input, it belongs in `artifacts/inputs/`.
- If it is generated proof/report output, it belongs in `evidence/`.
