# Monochromatic no-three-in-line: 18x18 case

This folder contains a reproducible working package for the monochromatic no-three-in-line problem on the `18 x 18` board.

The search is done on one checkerboard color class, here parity `0`, meaning points with `(x + y) mod 2 = 0`.

## Current result

This case is not closed yet.

The current recorded bounds are:

```text
27 <= D_mono(18) <= 28
```

The folder contains a verified 27-point configuration and several independent attempts to either find or rule out a 28-point configuration.

## Files

```text
18x18/
  README.md
  STATUS.md
  requirements.txt
  verify_config18.py
  dfs18.cpp
  cpsat18_triples.py
  minconf18.py
  milp18.py
  local18.py
  run_quick_check.sh
  run_quick_check.ps1
  data/
    lower_bound_27.json
    near_miss_28_local.json
    near_miss_28_minconf.json
  results/initial_runs/
    cpsat18.out
    dfs18.out
    local18.out
    milp18.out
    minconf18.out
```

## Verify the 27-point lower bound

From the repository root:

```bash
python 18x18/verify_config18.py 18x18/data/lower_bound_27.json
```

Expected result:

```text
OK: no three selected points lie on the same monochromatic line.
```

## Run the exact C++ DFS locally

```bash
cd 18x18
g++ -O3 -std=c++17 dfs18.cpp -o dfs18
./dfs18 300 0 1
```

Arguments:

```text
./dfs18 seconds shard_id shard_count
```

Examples:

```bash
./dfs18 300 0 1      # one normal run
./dfs18 300 0 8      # shard 0 of 8
./dfs18 300 1 8      # shard 1 of 8
```

The sharding is useful on GitHub Actions, where different jobs can search different first-row branches.

## Run CP-SAT and MILP locally

Install dependencies:

```bash
pip install -r 18x18/requirements.txt
```

Then run:

```bash
python 18x18/cpsat18_triples.py 300
python 18x18/minconf18.py 300
python 18x18/milp18.py 300
python 18x18/local18.py 300
```

## GitHub Actions

The package also includes:

```text
.github/workflows/n18-search.yml
```

After uploading this package to a public GitHub repository, open the `Actions` tab and run the workflow named `n18 search`.

Use `mode=smoke` for a short check.
Use `mode=deep` for a longer search with 8 DFS shards plus CP-SAT, minimum-conflict, and local search.

## How to close the case

A closure can happen in one of two ways:

1. A valid 28-point configuration is found and verified.
2. Exhaustive search or a certificate proves that no 28-point configuration exists.

At the moment this package does neither. It is a reproducible search package and a clean starting point for closing the `18x18` case.
