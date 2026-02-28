# Hello-Core Minimal Implementation: Immediate Next Steps

Status: COMPLETE

## Goal
Implement the minimal deterministic hello-core reference stack required to reproduce the golden artifacts.

## Step 1: Data Batching
- Implement `Glyphser.Data.NextBatch`.
- Target file: `runtime/glyphser/data/next_batch.py`.
- Inputs/outputs must match the operator signature in the operator registry.

## Step 2: Minimal Model Executor
- Implement `Glyphser.Model.ModelIR_Executor`.
- Target file: `runtime/glyphser/model/model_ir_executor.py`.

## Step 3: Trace Writer
- Implement trace sidecar writer with deterministic ordering.
- Target file: `runtime/glyphser/trace/trace_sidecar.py`.

## Step 4: Checkpoint Writer
- Implement `Glyphser.IO.SaveCheckpoint`.
- Target file: `runtime/glyphser/checkpoint/write.py`.

## Step 5: Execution Certificate
- Implement `Glyphser.Certificate.WriteExecutionCertificate`.
- Target file: `runtime/glyphser/certificate/build.py`.

## Step 6: Runner Script
- Create `tooling/scripts/run_hello_core.py` following `docs/START-HERE.md`.

## Gate
- Must reproduce `docs/examples/hello-core/hello-core-golden.json` hashes.
- If mismatch occurs: stop feature work, add vectors, fix determinism first.
