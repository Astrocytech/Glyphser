# Glyphser HTTP API (FastAPI) — REST Endpoints

This document describes the current REST endpoints exposed by the Glyphser demo HTTP API (`glyphser-api`).

Notes:
- All request/response bodies are JSON unless otherwise stated.
- Response shapes are considered **unstable** at this stage; the goal is broad functional coverage for the UI.
- Many endpoints wrap “deterministic / minimal” runtime modules in `runtime/glyphser/*`.
- When FastAPI is installed, OpenAPI docs are available at `GET /docs` and schema at `GET /openapi.json`.

---

## Run the server

Install API deps and run:

```bash
pip install -e ".[api]"
glyphser-api
```

Defaults: `127.0.0.1:8000`.

---

## Environment variables

Server:
- `GLYPHSER_HTTP_HOST` (default `127.0.0.1`)
- `GLYPHSER_HTTP_PORT` (default `8000`)
- `GLYPHSER_HTTP_RELOAD` (default `false`)
- `GLYPHSER_HTTP_REQUIRE_HTTPS` (default `false`)
- `GLYPHSER_HTTP_CORS_ORIGINS` (default `*`) — comma-separated list

Workspace roots:
- `GLYPHSER_HTTP_WORK_ROOT` (default `/tmp/glyphser_http_workspace`) — API writes doctor/setup/run/certify outputs, traces, certificates, checkpoints here.
- `GLYPHSER_HTTP_SNAPSHOT_ROOT` (default `/tmp/glyphser_snapshots`) — `/snapshot/write` writes here.

Runtime Jobs API backing store:
- `GLYPHSER_RUNTIME_API_ROOT` (default: repo root)
- `GLYPHSER_RUNTIME_API_STATE_PATH` (default `/tmp/glyphser_runtime_api/state.json`)
- `GLYPHSER_RUNTIME_API_AUDIT_LOG_PATH` (optional; otherwise uses `audit.log.jsonl` next to state)

---

## Auth model (runtime jobs)

The runtime jobs control plane endpoints expect:
- `token`: a string, often `role:<role>` for demo usage (for example `role:admin`)
- `scope`: one of `jobs:write`, `jobs:read`, `evidence:read`, `replay:run`

The server does not manage user sessions; the UI supplies token+scope per request.

---

## Endpoints

### Health / Info

- `GET /status`
  - Returns a simple status message.

- `GET /info`
  - Returns server + configured roots (workspace, snapshots, runtime API paths).

### Errors

Most errors are returned as an HTTP error status with a JSON body containing `detail`.
- `400` for invalid payloads / validation failures
- `403` for blocked operations (for example HTTPS required, path escape attempts)
- `500` for unexpected internal errors

### Verification

- `GET /verify/targets`
  - Lists supported verification fixture targets (currently: `hello-core`).

- `POST /verify`
  - Verify either a fixture target or a model IR.
  - Body (one of):
    - Fixture mode: `{ "target": "hello-core" }`
    - Model mode: `{ "model": { ... }, "input_data": { ... } }`

### Snapshots

- `POST /snapshot`
  - Builds a snapshot manifest (in-memory).
  - Body: `{ "model": { ... }, "input_data": { ... } }`

- `POST /snapshot/write`
  - Builds and writes a snapshot manifest under `GLYPHSER_HTTP_SNAPSHOT_ROOT`.
  - Body: `{ "model": { ... }, "input_data": { ... }, "name": "snapshot.json" }`

### Runtime CLI (doctor/setup/run/certify)

These endpoints emulate the runtime CLI workflows and write outputs under `GLYPHSER_HTTP_WORK_ROOT`.

- `POST /runtime/cli/doctor`
  - Body: `{ "run_id": "optional-string" }`

- `POST /runtime/cli/setup`
  - Body (doctor manifest is required via one of two ways):
    - Inline doctor manifest:
      ```json
      {
        "profile": "available_local",
        "doctor_manifest": { ... },
        "dry_run": false,
        "offline": false,
        "max_retries": 1,
        "timeout_sec": 300,
        "run_id": "optional-string"
      }
      ```
    - Reference an existing doctor run:
      ```json
      {
        "profile": "available_local",
        "doctor_run_id": "previous-doctor-run-id",
        "dry_run": true
      }
      ```

- `POST /runtime/cli/run`
  - Body (doctor manifest provided inline or via `doctor_run_id`):
    ```json
    {
      "profile": "auto",
      "doctor_run_id": "previous-doctor-run-id",
      "run_id": "optional-string"
    }
    ```

- `POST /runtime/cli/certify`
  - Body: `{ "profile": "available_local", "run_id": "optional-string" }`

### Runtime Jobs API (submit/status/evidence/replay)

- `POST /runtime/jobs/submit`
  - Body:
    ```json
    {
      "payload": { "payload": { }, "metadata": { }, "tags": [ ] },
      "token": "role:admin",
      "scope": "jobs:write",
      "idempotency_key": "optional"
    }
    ```

- `POST /runtime/jobs/status`
  - Body: `{ "job_id": "<id>", "token": "...", "scope": "jobs:read" }`

- `POST /runtime/jobs/evidence`
  - Body: `{ "job_id": "<id>", "token": "...", "scope": "evidence:read" }`

- `POST /runtime/jobs/replay`
  - Body: `{ "job_id": "<id>", "token": "...", "scope": "replay:run" }`

Debug/inspection:
- `GET /runtime/jobs/state`
  - Summarized view of runtime API state (jobs + quota counters) from `GLYPHSER_RUNTIME_API_STATE_PATH`.

- `GET /runtime/jobs/audit?limit=200`
  - Tails the audit log JSONL (defaults to `audit.log.jsonl` next to runtime state).

### Runtime API Tools

- `POST /runtime/api-tools/validate-signature`
  - Validates an API-interface signature record.
  - Body: `{ "record": { ... }, "allowed_ops": [ ... ] }` (`allowed_ops` optional)

- `POST /runtime/api-tools/classify-error`
  - Classifies an error string into a deterministic error code.
  - Body: `{ "message": "..." }`

### Runtime Tools (IR / contract / hashing / backend routing / registry)

- `POST /runtime/tools/ir/validate`
  - Validates and normalizes an IR DAG.
  - Body: `{ "ir_dag": { ... } }`

- `POST /runtime/tools/contract/validate`
  - Validates IR against a resolved driver’s supported instructions.
  - Body:
    ```json
    {
      "ir_dag": { ... },
      "driver_request": { "driver_id": "default" },
      "mode": "forward"
    }
    ```

- `POST /runtime/tools/trace/hash`
  - Computes a deterministic hash-chain over trace records.
  - Body: `{ "records": [ { ... }, { ... } ] }`

- `POST /runtime/tools/trace/write`
  - Writes a trace JSON file under `GLYPHSER_HTTP_WORK_ROOT/traces/`.
  - Body: `{ "records": [ ... ], "name": "trace.json" }`

- `POST /runtime/tools/certificate/write`
  - Writes an execution certificate under `GLYPHSER_HTTP_WORK_ROOT/certificates/`.
  - Body: `{ "evidence": { ... }, "name": "execution_certificate.json" }`

- `GET /runtime/tools/backend/routes`
  - Lists direct driver ids and pinned profile catalogs.

- `POST /runtime/tools/backend/policy`
  - Returns universal routing policy info for a request.
  - Body: `{ "request": { ... } }`

- `POST /runtime/tools/backend/load-driver`
  - Resolves a driver selection and returns deterministic driver metadata.
  - Body: `{ "request": { ... } }`

- `POST /runtime/tools/cert/evidence-validate`
  - Minimal deterministic evidence validation wrapper.
  - Body: `{ "request": { ... } }`

- `POST /runtime/tools/data/next-batch`
  - Pure helper for dataset paging.
  - Body: `{ "dataset": [ ... ], "cursor": 0, "batch_size": 32 }`

- `POST /runtime/tools/registry/interface-hash`
  - Computes the interface hash for a registry payload.
  - Body: `{ "registry": { ... } }`

- `GET /runtime/tools/registry/api-interfaces`
  - Parses the repository `API-Interfaces.md` and returns extracted operator rows.

### Runtime Ops (whitelisted generic dispatcher)

This is a “cover more code quickly” endpoint that dispatches a **whitelist** of deterministic/minimal runtime operations.

- `GET /runtime/ops`
  - Returns the list of allowed op strings.

- `POST /runtime/ops/{op}`
  - Body: `{ "request": { ... } }`
  - Current op whitelist:
    - `checkpoint.migrate_checkpoint`
    - `checkpoint.restore`
    - `config.manifest_migrate`
    - `dp.apply`
    - `legacy_import.legacy_framework_import`
    - `monitor.drift_compute`
    - `monitor.emit`
    - `monitor.register`
    - `registry.stage_transition`
    - `registry.version_create`
    - `tmmu.commit_execution`
    - `trace.migrate_trace`
    - `tracking.artifact_get`
    - `tracking.artifact_list`
    - `tracking.artifact_put`
    - `tracking.artifact_tombstone`
    - `tracking.metric_log`
    - `tracking.run_create`
    - `tracking.run_end`
    - `tracking.run_start`

### Checkpoints

- `POST /runtime/checkpoint/save`
  - Writes a checkpoint under `GLYPHSER_HTTP_WORK_ROOT/checkpoints/`.
  - Body: `{ "state": { ... }, "name": "checkpoint.json" }`

### Explorer (repo + workspace browsing)

- `GET /explorer/roots`
  - Returns allowed root labels and their absolute paths.
  - Root labels: `repo`, `docs`, `specs`, `artifacts`, `evidence`, `runtime`, `glyphser`, `workspace`

- `GET /explorer/list?root=<label>&path=<relpath>`
  - Lists directory entries under a root.

- `GET /explorer/read?root=<label>&path=<relpath>`
  - Reads a text file under a root (size-limited).

---

## Quick curl examples

```bash
curl -s http://127.0.0.1:8000/status
```

```bash
curl -s http://127.0.0.1:8000/verify/targets
```

```bash
curl -s http://127.0.0.1:8000/verify \
  -H 'Content-Type: application/json' \
  -d '{"target":"hello-core"}'
```

```bash
curl -s http://127.0.0.1:8000/runtime/jobs/submit \
  -H 'Content-Type: application/json' \
  -d '{"payload":{"payload":{}}, "token":"role:admin", "scope":"jobs:write"}'
```
