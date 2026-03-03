# Docker Quickstart

Build and run Glyphser with a deterministic hello-core check.

## Build

```bash
docker build -t glyphser:local .
```

## Run

```bash
docker run --rm glyphser:local
```

Expected output includes:
- `VERIFY hello-core: PASS`
- Trace/certificate/interface hashes
- evidence file paths
