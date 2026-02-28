# API Style Guide (Milestone 18)

## Naming and Casing
- Endpoints use lowercase path segments.
- JSON field names use `snake_case`.
- Resource identifiers use stable string IDs (`job_id`).

## Error Envelope
- Errors must use a stable envelope:
- `code`: machine-readable error code.
- `message`: short human-readable explanation.
- `trace_id`: deterministic request trace identifier.
- `details`: optional structured diagnostics.

## Versioning
- Public endpoints are namespace-versioned (`/v1/...`).
- Breaking changes require major version increment.

## Idempotency
- Create/submit endpoints must accept `X-Idempotency-Key`.
- Repeated requests with same key must return same logical job identity.

## Traceability
- Every request/response pair must carry a deterministic trace identifier.
