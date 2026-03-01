package main

import (
	"encoding/json"
	"fmt"
	"os"
	"strconv"
	"strings"
)

func parseCSV(csv string) ([]float64, error) {
	if strings.TrimSpace(csv) == "" {
		return []float64{}, nil
	}
	parts := strings.Split(csv, ",")
	out := make([]float64, len(parts))
	for i, p := range parts {
		v, err := strconv.ParseFloat(strings.TrimSpace(p), 64)
		if err != nil {
			return nil, err
		}
		out[i] = v
	}
	return out, nil
}

func main() {
	if len(os.Args) != 4 {
		fmt.Fprintln(os.Stderr, "usage: GoLaneRunner <input_csv> <weights_csv> <bias>")
		os.Exit(2)
	}
	input, err := parseCSV(os.Args[1])
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(3)
	}
	weights, err := parseCSV(os.Args[2])
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(3)
	}
	bias, err := strconv.ParseFloat(os.Args[3], 64)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(3)
	}
	if len(input) != len(weights) {
		fmt.Fprintln(os.Stderr, "input and weights length mismatch")
		os.Exit(4)
	}
	sum := 0.0
	for i := range input {
		sum += input[i] * weights[i]
	}
	output := sum + bias
	payload := map[string]any{
		"runtime":         "go_cpu",
		"runtime_version": "unknown",
		"outputs":         [][]float64{{output}},
	}
	enc := json.NewEncoder(os.Stdout)
	if err := enc.Encode(payload); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(5)
	}
}
