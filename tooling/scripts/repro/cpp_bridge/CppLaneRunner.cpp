#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

static std::vector<double> parse_csv(const std::string& csv) {
  std::vector<double> out;
  std::stringstream ss(csv);
  std::string part;
  while (std::getline(ss, part, ',')) {
    if (!part.empty()) {
      out.push_back(std::stod(part));
    }
  }
  return out;
}

int main(int argc, char** argv) {
  if (argc != 4) {
    std::cerr << "usage: CppLaneRunner <input_csv> <weights_csv> <bias>\n";
    return 2;
  }
  auto input = parse_csv(argv[1]);
  auto weights = parse_csv(argv[2]);
  double bias = std::stod(argv[3]);
  if (input.size() != weights.size()) {
    std::cerr << "input and weights length mismatch\n";
    return 4;
  }
  double sum = 0.0;
  for (size_t i = 0; i < input.size(); ++i) {
    sum += input[i] * weights[i];
  }
  double out = sum + bias;
  std::cout << std::setprecision(17)
            << "{\"runtime\":\"cpp_cpu\",\"runtime_version\":\"unknown\",\"outputs\":[[" << out << "]]}\n";
  return 0;
}
