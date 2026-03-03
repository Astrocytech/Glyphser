# Evidence Lifecycle

Glyphser evidence lifecycle has four stages:

1. Generate: produce evidence via `make release-check`.
2. Catalog: record canonical metadata in `evidence/metadata/catalog.json`.
3. Validate: run metadata/schema gates.
4. Archive: snapshot and retain evidence history with bounded retention.

## Archive command

```bash
python tooling/release/archive_evidence.py --keep 10
```

## Archive outputs

- Snapshot directories: `evidence/archive/<timestamp>/...`
- Archive index: `evidence/archive/index.json`

## Retention policy

- Keep latest N snapshots (`--keep` argument).
- Oldest snapshots are pruned automatically.
