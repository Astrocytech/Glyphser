# Start Here (Day 1 Contributor Pathway)

This guide takes a new contributor from clone to verified deterministic evidence in one sitting.

## Milestone 0: Environment Ready

Command:

```bash
python tooling/commands/bootstrap_dev.py --verify
```

Expected:
- Generates `evidence/dev/bootstrap.json`
- Status is `PASS` (or actionable failures with command output)

## Milestone 1: First Deterministic Run

Command:

```bash
glyphser run --example hello --tree
```

Expected:
- `VERIFY hello-core: PASS`
- Trace/certificate/interface hashes printed
- Evidence files shown under `artifacts/inputs/fixtures/hello-core/`

## Milestone 2: Validate Core Quality Gates

Command:

```bash
make gates
```

Expected:
- `SPEC_IMPL_CONGRUENCE_GATE: PASS`

## Milestone 3: Generate Traceability + Evidence Catalog

Command:

```bash
make traceability
make evidence-metadata
```

Expected:
- `evidence/traceability/index.json` exists
- `EVIDENCE_METADATA_GATE: PASS`
- `evidence/metadata/catalog.json` exists

## Milestone 4: Full Internal Release Check

Command:

```bash
make release-check
```

Expected:
- test suite passes
- benchmark artifacts generated
- congruence + traceability + metadata checks pass
- final line: `release-check: PASS`

## Milestone 5: Make a Safe First Change

1. Pick a `good first issue` from `docs/ISSUE_BACKLOG.md`.
2. Implement a small change.
3. Run:

```bash
pytest -q
make release-check
```

4. Open PR using `.github/PULL_REQUEST_TEMPLATE.md`.

## Where to look next

- Architecture: `docs/ARCHITECTURE.md`
- Spec/code contract map: `docs/SPEC_IMPLEMENTATION_MATRIX.md`
- Traceability model: `docs/TRACEABILITY.md`
- Integrations: `docs/INTEGRATIONS.md`
