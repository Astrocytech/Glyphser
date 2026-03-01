# Milestone 13 Java Runtime Hardening

This folder contains Java lane runners used by:

- `tooling/scripts/repro/compare_java_runtime_hardening.py`

Runners:

- `OnnxRuntimeLaneRunner.java` (expects ONNX Runtime Java on classpath)
- `DjlLaneRunner.java` (expects DJL on classpath)

## 1) Compile Runners

From repo root:

```bash
javac tooling/scripts/repro/java_bridge/OnnxRuntimeLaneRunner.java
javac tooling/scripts/repro/java_bridge/DjlLaneRunner.java
```

## 2) Install Java Dependencies (Maven local repo)

Example Linux commands:

```bash
mvn -q dependency:get -Dartifact=com.microsoft.onnxruntime:onnxruntime:1.20.0
mvn -q dependency:get -Dartifact=ai.djl:api:0.30.0
```

Example Windows `cmd` commands:

```bat
mvn -q dependency:get -Dartifact=com.microsoft.onnxruntime:onnxruntime:1.20.0
mvn -q dependency:get -Dartifact=ai.djl:api:0.30.0
```

## 3) Build Classpaths

Linux:

```bash
export GLYPHSER_ONNX_CLASSPATH="$HOME/.m2/repository/com/microsoft/onnxruntime/onnxruntime/1.20.0/onnxruntime-1.20.0.jar"
export GLYPHSER_DJL_CLASSPATH="$HOME/.m2/repository/ai/djl/api/0.30.0/api-0.30.0.jar"
```

Windows `cmd`:

```bat
set GLYPHSER_ONNX_CLASSPATH=%USERPROFILE%\.m2\repository\com\microsoft\onnxruntime\onnxruntime\1.20.0\onnxruntime-1.20.0.jar
set GLYPHSER_DJL_CLASSPATH=%USERPROFILE%\.m2\repository\ai\djl\api\0.30.0\api-0.30.0.jar
```

## 4) Run Milestone 13 Matrix

Linux:

```bash
./.venv/bin/python tooling/scripts/repro/compare_java_runtime_hardening.py \
  --onnx-classpath "$GLYPHSER_ONNX_CLASSPATH" \
  --djl-classpath "$GLYPHSER_DJL_CLASSPATH"
```

Windows `cmd`:

```bat
.venv\Scripts\python.exe tooling\scripts\repro\compare_java_runtime_hardening.py --onnx-classpath "%GLYPHSER_ONNX_CLASSPATH%" --djl-classpath "%GLYPHSER_DJL_CLASSPATH%"
```

Artifacts are written to:

- `evidence/repro/milestone-13-java-runtime-hardening/`
