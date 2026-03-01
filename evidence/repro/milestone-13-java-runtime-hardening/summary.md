# Milestone 13: Java Runtime Hardening

Status: PASS
Classification: E1
Reason: All PyTorch↔Java runtime hardening pairs pass.

## Java Runtime Lanes
- onnxruntime_java
- djl

## Required Inputs
- Option A: provide --onnx-java-cmd and --djl-java-cmd templates.
- Option B: provide --onnx-classpath and --djl-classpath; defaults build commands automatically.
- Placeholder support for explicit templates: {input_csv}, {weights_csv}, {bias}.
