using System;
using System.Globalization;
using System.Linq;

public static class CSharpLaneRunner
{
    private static double[] ParseCsv(string csv)
    {
        if (string.IsNullOrWhiteSpace(csv))
        {
            return Array.Empty<double>();
        }
        return csv.Split(',')
            .Select(p => double.Parse(p.Trim(), CultureInfo.InvariantCulture))
            .ToArray();
    }

    public static int Main(string[] args)
    {
        if (args.Length != 3)
        {
            Console.Error.WriteLine("usage: CSharpLaneRunner <input_csv> <weights_csv> <bias>");
            return 2;
        }

        double[] input = ParseCsv(args[0]);
        double[] weights = ParseCsv(args[1]);
        double bias = double.Parse(args[2], CultureInfo.InvariantCulture);
        if (input.Length != weights.Length)
        {
            Console.Error.WriteLine("input and weights length mismatch");
            return 4;
        }

        double sum = 0.0;
        for (int i = 0; i < input.Length; i++)
        {
            sum += input[i] * weights[i];
        }

        double output = sum + bias;
        Console.WriteLine("{\"runtime\":\"csharp_cpu\",\"runtime_version\":\"unknown\",\"outputs\":[[" +
                          output.ToString("R", CultureInfo.InvariantCulture) + "]]}");
        return 0;
    }
}
