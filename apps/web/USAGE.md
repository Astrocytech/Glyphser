# Glyphser Verification Console - Usage Guide

## Quick Start

### 1. Start the Backend

```bash
cd /home/njonji/Desktop/ASTROCYTECH/Glyphser
python -m glyphser.http_api.main
```

### 2. Start the Frontend

```bash
cd apps/web
npm run dev
```

Navigate to `http://localhost:5173`.

## Console Pages

- **Dashboard** - Overview of verification system
- **Verify** - Verify models and fixtures
- **Runs** - View and manage verification runs
- **Artifacts** - Browse run artifacts
- **Jobs API** - Runtime jobs (Submit, Status, Evidence, Replay)
- **Doctor** - Inspect machine capabilities
- **Setup** - Plan setup configurations
- **Route Run** - Select deterministic routes
- **Certify** - Generate certifications
- **Conformance** - Review gates and verdicts
- **API Tools** - Validate signatures, classify errors
- **Explorer** - Browse runtime modules
- **Docs** - Read documentation
- **Settings** - Configure preferences
