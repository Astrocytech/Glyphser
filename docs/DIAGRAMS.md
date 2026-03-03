# Diagrams

## Deterministic Verification Flow

```text
Model + Inputs
    |
    v
Glyphser Verify
    |
    +--> Runtime Execution
    |
    +--> Canonical Hashing
    |
    +--> Evidence Manifests
    |
    v
PASS/FAIL + Digests + Evidence Paths
```

## Evidence Issuance

```text
Trace Records ----> trace_final_hash
Checkpoint -------> checkpoint_hash
Contracts --------> interface_hash
                    |
                    v
            execution_certificate.json
```
