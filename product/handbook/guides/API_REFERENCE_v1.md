# API Reference v1

Source contract: `specs/contracts/openapi_public_api_v1.yaml`

## Endpoints
- `POST /v1/jobs`: submit job request (supports `X-Idempotency-Key`).
- `GET /v1/jobs/{job_id}`: fetch job status.
- `GET /v1/jobs/{job_id}/evidence`: fetch evidence hashes and pointers.
- `POST /v1/jobs/{job_id}/replay`: execute replay-verdict check.

## Authentication
- Bearer token required for all endpoints.

## Versioning
- API namespace: `/v1`.
- Contract version: `1.0.0`.
- Breaking changes require major version increment.

## CLI Mapping
- `submit` -> `POST /v1/jobs`
- `status` -> `GET /v1/jobs/{job_id}`
- `evidence` -> `GET /v1/jobs/{job_id}/evidence`
- `replay` -> `POST /v1/jobs/{job_id}/replay`
