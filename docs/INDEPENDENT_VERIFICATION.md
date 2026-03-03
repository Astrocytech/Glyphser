# Independent Verification

This procedure validates a deterministic fixture without trusting a pre-existing local state.

## Steps

1. Checkout repository at a tagged commit.
2. Run:

```bash
glyphser verify hello-core --format json
```

3. Confirm returned `actual` values match `expected` values.
4. Confirm evidence files exist in `artifacts/inputs/fixtures/hello-core/`.

## Manual digest checks

```bash
python - <<'PY'
import json, hashlib
from pathlib import Path
from runtime.glyphser.trace.compute_trace_hash import compute_trace_hash

root = Path('artifacts/inputs/fixtures/hello-core')
trace = json.loads((root / 'trace.json').read_text())
cert = json.loads((root / 'execution_certificate.json').read_text())
print('trace_final_hash', compute_trace_hash(trace))
print('certificate_hash', hashlib.sha256(json.dumps(cert, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()).hexdigest())
PY
```
