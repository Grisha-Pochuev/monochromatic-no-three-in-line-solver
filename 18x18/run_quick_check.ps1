Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot
python verify_config18.py data/lower_bound_27.json

g++ -O3 -std=c++17 dfs18.cpp -o dfs18.exe
./dfs18.exe 30 0 1 > results/quick_dfs18.out 2> results/quick_dfs18.log
python local18.py 30 > results/quick_local18.out 2> results/quick_local18.log

Write-Host "Quick check finished. See 18x18/results/."
