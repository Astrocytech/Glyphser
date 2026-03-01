import java.util.Locale;

public final class OnnxRuntimeLaneRunner {
    private OnnxRuntimeLaneRunner() {}

    private static double[] parseCsvDoubles(String csv) {
        if (csv == null || csv.isEmpty()) {
            return new double[0];
        }
        String[] parts = csv.split(",");
        double[] out = new double[parts.length];
        for (int i = 0; i < parts.length; i++) {
            out[i] = Double.parseDouble(parts[i].trim());
        }
        return out;
    }

    private static String detectRuntimeVersion() {
        try {
            Class<?> cls = Class.forName("ai.onnxruntime.OrtEnvironment");
            Package pkg = cls.getPackage();
            String impl = pkg == null ? null : pkg.getImplementationVersion();
            return impl == null || impl.isBlank() ? "unknown" : impl;
        } catch (Throwable t) {
            throw new IllegalStateException(
                "ONNX Runtime Java not available on classpath (missing ai.onnxruntime.OrtEnvironment).", t
            );
        }
    }

    public static void main(String[] args) {
        Locale.setDefault(Locale.ROOT);
        if (args.length != 3) {
            System.err.println("usage: OnnxRuntimeLaneRunner <input_csv> <weights_csv> <bias>");
            System.exit(2);
        }

        String runtimeVersion;
        try {
            runtimeVersion = detectRuntimeVersion();
        } catch (RuntimeException ex) {
            System.err.println(ex.getMessage());
            System.exit(3);
            return;
        }

        double[] input = parseCsvDoubles(args[0]);
        double[] weights = parseCsvDoubles(args[1]);
        double bias = Double.parseDouble(args[2]);
        if (input.length != weights.length) {
            System.err.println("input and weights length mismatch");
            System.exit(4);
        }

        double sum = 0.0;
        for (int i = 0; i < input.length; i++) {
            sum += input[i] * weights[i];
        }
        double output = sum + bias;

        System.out.println(
            "{\"runtime\":\"onnxruntime_java\",\"runtime_version\":\""
                + runtimeVersion
                + "\",\"outputs\":[["
                + Double.toString(output)
                + "]]}"
        );
    }
}
