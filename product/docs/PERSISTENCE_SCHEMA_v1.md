# Persistence Schema v1 (Milestone 19)

## Scope
Schema used for durable runtime state, WAL records, and checkpoints.

## State File (`state.json`)
```json
{
  "schema_version": 1,
  "state": {
    "events": [ ... ],
    "last_event_hash": "..."
  }
}
```

## WAL File (`wal.jsonl`)
Each line:
```json
{
  "schema_version": 1,
  "event": { ... },
  "event_hash": "sha256hex"
}
```

## Checkpoint File (`checkpoint.json`)
```json
{
  "schema_version": 1,
  "state": { ... },
  "state_hash": "sha256hex"
}
```

## Versioning Rules
- `schema_version=1` is current baseline.
- Any incompatible field/semantic change requires schema version increment.
- Restore/migrate path must be explicit for non-current schema versions.

