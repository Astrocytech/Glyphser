import java.util.Locale;

public class ModelClassExpansionJavaRunner {
    private static double[] parseVector(String csv) {
        if (csv == null || csv.isEmpty()) {
            return new double[0];
        }
        String[] parts = csv.split(",");
        double[] out = new double[parts.length];
        for (int i = 0; i < parts.length; i++) {
            out[i] = Double.parseDouble(parts[i]);
        }
        return out;
    }

    private static String formatDouble(double x) {
        return String.format(Locale.US, "%.17g", x);
    }

    private static String vectorJson(double[] v) {
        StringBuilder sb = new StringBuilder();
        sb.append("[");
        for (int i = 0; i < v.length; i++) {
            if (i > 0) sb.append(",");
            sb.append(formatDouble(v[i]));
        }
        sb.append("]");
        return sb.toString();
    }

    private static double[] dense(double[] x, double[][] w, double[] b) {
        double[] out = new double[w.length];
        for (int i = 0; i < w.length; i++) {
            double acc = 0.0;
            for (int j = 0; j < x.length; j++) {
                acc += w[i][j] * x[j];
            }
            out[i] = acc + b[i];
        }
        return out;
    }

    private static double[] relu(double[] x) {
        double[] out = new double[x.length];
        for (int i = 0; i < x.length; i++) {
            out[i] = Math.max(0.0, x[i]);
        }
        return out;
    }

    private static double[] sigmoid(double[] x) {
        double[] out = new double[x.length];
        for (int i = 0; i < x.length; i++) {
            out[i] = 1.0 / (1.0 + Math.exp(-x[i]));
        }
        return out;
    }

    private static double[] conv1dValid(double[] x, double[] k, double bias) {
        int outLen = x.length - k.length + 1;
        double[] out = new double[outLen];
        for (int i = 0; i < outLen; i++) {
            double acc = 0.0;
            for (int j = 0; j < k.length; j++) {
                acc += x[i + j] * k[j];
            }
            out[i] = acc + bias;
        }
        return out;
    }

    private static double[][] matmul2x2(double[][] a, double[][] b) {
        double[][] out = new double[2][2];
        for (int i = 0; i < 2; i++) {
            for (int j = 0; j < 2; j++) {
                out[i][j] = a[i][0] * b[0][j] + a[i][1] * b[1][j];
            }
        }
        return out;
    }

    private static double[][] transpose2x2(double[][] a) {
        return new double[][] {{a[0][0], a[1][0]}, {a[0][1], a[1][1]}};
    }

    private static double[] softmax(double[] x) {
        double max = x[0];
        for (int i = 1; i < x.length; i++) max = Math.max(max, x[i]);
        double[] exp = new double[x.length];
        double sum = 0.0;
        for (int i = 0; i < x.length; i++) {
            exp[i] = Math.exp(x[i] - max);
            sum += exp[i];
        }
        for (int i = 0; i < x.length; i++) exp[i] /= sum;
        return exp;
    }

    private static double[][] softmaxRows2x2(double[][] x) {
        return new double[][] {softmax(x[0]), softmax(x[1])};
    }

    private static double reduceSum2x2(double[][] x) {
        return x[0][0] + x[0][1] + x[1][0] + x[1][1];
    }

    public static void main(String[] args) {
        try {
            if (args.length < 2) {
                throw new IllegalArgumentException("usage: <model_id> <input_csv>");
            }
            String model = args[0];
            double[] input = parseVector(args[1]);
            double[] out;

            switch (model) {
                case "mlp_deep": {
                    double[][] w1 = {
                        {0.2, -0.1, 0.4, 0.3},
                        {-0.3, 0.8, -0.2, 0.1},
                        {0.5, 0.2, -0.5, 0.7},
                        {0.6, -0.4, 0.1, 0.2}
                    };
                    double[] b1 = {0.1, -0.2, 0.05, 0.0};
                    double[][] w2 = {
                        {0.7, -0.1, 0.2, 0.3},
                        {-0.2, 0.5, 0.4, -0.6},
                        {0.1, 0.2, -0.3, 0.9}
                    };
                    double[] b2 = {0.01, -0.03, 0.02};
                    out = sigmoid(dense(relu(dense(input, w1, b1)), w2, b2));
                    break;
                }
                case "cnn_tiny": {
                    double[] k = {0.25, -0.5, 0.75};
                    double b = 0.1;
                    double[] conv = relu(conv1dValid(input, k, b));
                    double[][] w = {
                        {0.6, -0.2, 0.1, 0.5},
                        {-0.3, 0.7, 0.2, -0.4}
                    };
                    double[] b2 = {0.05, -0.08};
                    out = dense(conv, w, b2);
                    break;
                }
                case "attention_lite": {
                    double[][] x = {
                        {input[0], input[1]},
                        {input[2], input[3]}
                    };
                    double[][] scores = matmul2x2(x, transpose2x2(x));
                    double[][] attn = softmaxRows2x2(scores);
                    double[][] ctx = matmul2x2(attn, x);
                    out = new double[] {reduceSum2x2(ctx)};
                    break;
                }
                default:
                    throw new IllegalArgumentException("unsupported model: " + model);
            }

            System.out.println("{\"outputs\":[" + vectorJson(out) + "]}");
        } catch (Exception e) {
            System.err.println(e.getMessage());
            System.exit(1);
        }
    }
}
