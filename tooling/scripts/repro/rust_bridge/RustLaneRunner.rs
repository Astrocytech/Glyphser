use std::env;
use std::process;

fn parse_csv_f64(csv: &str) -> Result<Vec<f64>, String> {
    if csv.trim().is_empty() {
        return Ok(Vec::new());
    }
    csv.split(',')
        .map(|s| s.trim().parse::<f64>().map_err(|e| format!("parse float error: {e}")))
        .collect()
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() != 4 {
        eprintln!("usage: RustLaneRunner <input_csv> <weights_csv> <bias>");
        process::exit(2);
    }

    let input = match parse_csv_f64(&args[1]) {
        Ok(v) => v,
        Err(e) => {
            eprintln!("{e}");
            process::exit(3);
        }
    };
    let weights = match parse_csv_f64(&args[2]) {
        Ok(v) => v,
        Err(e) => {
            eprintln!("{e}");
            process::exit(3);
        }
    };
    let bias = match args[3].parse::<f64>() {
        Ok(v) => v,
        Err(e) => {
            eprintln!("parse bias error: {e}");
            process::exit(3);
        }
    };

    if input.len() != weights.len() {
        eprintln!("input and weights length mismatch");
        process::exit(4);
    }

    let dot: f64 = input.iter().zip(weights.iter()).map(|(x, w)| x * w).sum();
    let output = dot + bias;

    println!(
        "{{\"runtime\":\"rust_cpu\",\"runtime_version\":\"{}\",\"outputs\":[[{}]]}}",
        "unknown",
        output
    );
}
