# Milestone 14 Rust Bridge

This folder contains the Rust lane runner used by:

- `tooling/scripts/repro/compare_additional_language_bridges.py`

## Compile Runner

From repo root:

```bash
rustc tooling/scripts/repro/rust_bridge/RustLaneRunner.rs -O -o tooling/scripts/repro/rust_bridge/RustLaneRunner
```

Windows `cmd`:

```bat
rustc tooling\scripts\repro\rust_bridge\RustLaneRunner.rs -O -o tooling\scripts\repro\rust_bridge\RustLaneRunner.exe
```

## Run Milestone 14

Linux:

```bash
./.venv/bin/python tooling/scripts/repro/compare_additional_language_bridges.py \
  --onnx-classpath "$GLYPHSER_ONNX_CLASSPATH" \
  --djl-classpath "$GLYPHSER_DJL_CLASSPATH"
```

Windows `cmd`:

```bat
.venv\Scripts\python.exe tooling\scripts\repro\compare_additional_language_bridges.py --onnx-classpath "%GLYPHSER_ONNX_CLASSPATH%" --djl-classpath "%GLYPHSER_DJL_CLASSPATH%"
```

Artifacts are written to:

- `evidence/repro/milestone-14-additional-language-bridges/`
