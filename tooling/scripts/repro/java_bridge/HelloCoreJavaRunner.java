import java.util.Locale;

public final class HelloCoreJavaRunner {
    private HelloCoreJavaRunner() {}

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

    public static void main(String[] args) {
        Locale.setDefault(Locale.ROOT);
        if (args.length != 3) {
            System.err.println("usage: HelloCoreJavaRunner <input_csv> <weights_csv> <bias>");
            System.exit(2);
        }

        double[] input = parseCsvDoubles(args[0]);
        double[] weights = parseCsvDoubles(args[1]);
        double bias = Double.parseDouble(args[2]);
        if (input.length != weights.length) {
            System.err.println("input and weights length mismatch");
            System.exit(3);
        }

        double sum = 0.0;
        for (int i = 0; i < input.length; i++) {
            sum += input[i] * weights[i];
        }
        double output = sum + bias;
        System.out.println("{\"outputs\":[[" + Double.toString(output) + "]]}");
    }
}
