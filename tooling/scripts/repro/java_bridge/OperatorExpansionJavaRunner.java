import java.util.Locale;

public class OperatorExpansionJavaRunner {
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

    private static double[][] parseMatrix(String csv, int rows, int cols) {
        double[] flat = parseVector(csv);
        if (flat.length != rows * cols) {
            throw new IllegalArgumentException("matrix size mismatch");
        }
        double[][] out = new double[rows][cols];
        int idx = 0;
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                out[r][c] = flat[idx++];
            }
        }
        return out;
    }

    private static String vectorJson(double[] v) {
        StringBuilder sb = new StringBuilder();
        sb.append("[");
        for (int i = 0; i < v.length; i++) {
            if (i > 0) {
                sb.append(",");
            }
            sb.append(formatDouble(v[i]));
        }
        sb.append("]");
        return sb.toString();
    }

    private static String matrixJson(double[][] m) {
        StringBuilder sb = new StringBuilder();
        sb.append("[");
        for (int r = 0; r < m.length; r++) {
            if (r > 0) {
                sb.append(",");
            }
            sb.append(vectorJson(m[r]));
        }
        sb.append("]");
        return sb.toString();
    }

    private static String formatDouble(double x) {
        return String.format(Locale.US, "%.17g", x);
    }

    private static double[] softmax(double[] x) {
        double max = x[0];
        for (int i = 1; i < x.length; i++) {
            if (x[i] > max) {
                max = x[i];
            }
        }
        double[] exp = new double[x.length];
        double sum = 0.0;
        for (int i = 0; i < x.length; i++) {
            exp[i] = Math.exp(x[i] - max);
            sum += exp[i];
        }
        for (int i = 0; i < x.length; i++) {
            exp[i] = exp[i] / sum;
        }
        return exp;
    }

    private static double[] layerNorm(double[] x, double[] gamma, double[] beta, double eps) {
        double mean = 0.0;
        for (double v : x) {
            mean += v;
        }
        mean /= x.length;
        double var = 0.0;
        for (double v : x) {
            double d = v - mean;
            var += d * d;
        }
        var /= x.length;
        double denom = Math.sqrt(var + eps);
        double[] out = new double[x.length];
        for (int i = 0; i < x.length; i++) {
            out[i] = ((x[i] - mean) / denom) * gamma[i] + beta[i];
        }
        return out;
    }

    public static void main(String[] args) {
        try {
            if (args.length < 1) {
                throw new IllegalArgumentException("missing op");
            }
            String op = args[0];
            String output;

            switch (op) {
                case "matmul": {
                    int aRows = Integer.parseInt(args[1]);
                    int aCols = Integer.parseInt(args[2]);
                    double[][] a = parseMatrix(args[3], aRows, aCols);
                    int bRows = Integer.parseInt(args[4]);
                    int bCols = Integer.parseInt(args[5]);
                    double[][] b = parseMatrix(args[6], bRows, bCols);
                    if (aCols != bRows) {
                        throw new IllegalArgumentException("matmul shape mismatch");
                    }
                    double[][] out = new double[aRows][bCols];
                    for (int i = 0; i < aRows; i++) {
                        for (int j = 0; j < bCols; j++) {
                            double acc = 0.0;
                            for (int k = 0; k < aCols; k++) {
                                acc += a[i][k] * b[k][j];
                            }
                            out[i][j] = acc;
                        }
                    }
                    output = matrixJson(out);
                    break;
                }
                case "reducesum": {
                    double[] v = parseVector(args[1]);
                    double sum = 0.0;
                    for (double x : v) {
                        sum += x;
                    }
                    output = "[" + formatDouble(sum) + "]";
                    break;
                }
                case "reshape": {
                    int rows = Integer.parseInt(args[1]);
                    int cols = Integer.parseInt(args[2]);
                    double[] v = parseVector(args[3]);
                    if (v.length != rows * cols) {
                        throw new IllegalArgumentException("reshape size mismatch");
                    }
                    double[][] out = new double[rows][cols];
                    int idx = 0;
                    for (int r = 0; r < rows; r++) {
                        for (int c = 0; c < cols; c++) {
                            out[r][c] = v[idx++];
                        }
                    }
                    output = matrixJson(out);
                    break;
                }
                case "transpose": {
                    int rows = Integer.parseInt(args[1]);
                    int cols = Integer.parseInt(args[2]);
                    double[][] m = parseMatrix(args[3], rows, cols);
                    double[][] out = new double[cols][rows];
                    for (int r = 0; r < rows; r++) {
                        for (int c = 0; c < cols; c++) {
                            out[c][r] = m[r][c];
                        }
                    }
                    output = matrixJson(out);
                    break;
                }
                case "softmax": {
                    double[] v = parseVector(args[1]);
                    output = vectorJson(softmax(v));
                    break;
                }
                case "layernorm": {
                    double[] x = parseVector(args[1]);
                    double[] gamma = parseVector(args[2]);
                    double[] beta = parseVector(args[3]);
                    double eps = Double.parseDouble(args[4]);
                    if (x.length != gamma.length || x.length != beta.length) {
                        throw new IllegalArgumentException("layernorm size mismatch");
                    }
                    output = vectorJson(layerNorm(x, gamma, beta, eps));
                    break;
                }
                case "mseloss": {
                    double[] pred = parseVector(args[1]);
                    double[] target = parseVector(args[2]);
                    if (pred.length != target.length) {
                        throw new IllegalArgumentException("mseloss size mismatch");
                    }
                    double acc = 0.0;
                    for (int i = 0; i < pred.length; i++) {
                        double d = pred[i] - target[i];
                        acc += d * d;
                    }
                    double mse = acc / pred.length;
                    output = "[" + formatDouble(mse) + "]";
                    break;
                }
                default:
                    throw new IllegalArgumentException("unsupported op: " + op);
            }

            System.out.println("{\"outputs\":[" + output + "]}");
        } catch (Exception e) {
            System.err.println(e.getMessage());
            System.exit(1);
        }
    }
}
