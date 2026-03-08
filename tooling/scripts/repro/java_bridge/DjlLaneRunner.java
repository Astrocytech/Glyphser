import java.util.Locale;

public final class DjlLaneRunner {
    private DjlLaneRunner() {}

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
            Class<?> cls = Class.forName("ai.djl.Model");
            Package pkg = cls.getPackage();
            String impl = pkg == null ? null : pkg.getImplementationVersion();
            return impl == null || impl.isBlank() ? "unknown" : impl;
        } catch (Throwable t) {
            throw new IllegalStateException("DJL not available on classpath (missing ai.djl.Model).", t);
        }
    }

    public static void main(String[] args) {
        Locale.setDefault(Locale.ROOT);
        if (args.length != 3) {
            System.err.println("usage: DjlLaneRunner <input_csv> <weights_csv> <bias>");
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
            "{\"runtime\":\"djl\",\"runtime_version\":\""
                + runtimeVersion
                + "\",\"outputs\":[["
                + Double.toString(output)
                + "]]}"
        );
    }
}
