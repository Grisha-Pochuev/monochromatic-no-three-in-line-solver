#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
python3 verify_config18.py data/lower_bound_27.json

g++ -O3 -std=c++17 dfs18.cpp -o dfs18
./dfs18 30 0 1 > results/quick_dfs18.out 2> results/quick_dfs18.log || true
python3 local18.py 30 > results/quick_local18.out 2> results/quick_local18.log || true

echo "Quick check finished. See 18x18/results/."
