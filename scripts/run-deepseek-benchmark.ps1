param(
  [ValidateSet("smoke", "long-context", "repair", "all")]
  [string]$SuiteSet = "smoke",
  [string]$OutputDir = "eval-runs/deepseek-benchmark",
  [string]$Python = "python",
  [switch]$IncludeMissingKey
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $RepoRoot

if ($env:PYTHONPATH) {
  $env:PYTHONPATH = "src;$env:PYTHONPATH"
} else {
  $env:PYTHONPATH = "src"
}

if (-not $IncludeMissingKey -and [string]::IsNullOrWhiteSpace($env:DEEPSEEK_API_KEY)) {
  throw "DEEPSEEK_API_KEY is missing. Set it in this PowerShell session before running the DeepSeek benchmark."
}

$runs = @()

if ($SuiteSet -eq "smoke" -or $SuiteSet -eq "all") {
  $runs += [pscustomobject]@{
    Name = "smoke"
    Suite = "model-labs/deepseek/deepseek-v4-suite.json"
    Comparison = "benchmarks/real-provider-comparison/provider-comparison.md"
    MaxSteps = 8
    ContextChars = 8000
    AllowWrite = $false
  }
}

if ($SuiteSet -eq "long-context" -or $SuiteSet -eq "all") {
  $runs += [pscustomobject]@{
    Name = "long-context"
    Suite = "model-labs/deepseek/deepseek-v4-long-context-suite.json"
    Comparison = "model-labs/deepseek/reports/long-context-comparison.md"
    MaxSteps = 10
    ContextChars = 24000
    AllowWrite = $false
  }
}

if ($SuiteSet -eq "repair" -or $SuiteSet -eq "all") {
  $runs += [pscustomobject]@{
    Name = "repair"
    Suite = "model-labs/deepseek/deepseek-v4-repair-suite.json"
    Comparison = "model-labs/deepseek/reports/repair-comparison.md"
    MaxSteps = 12
    ContextChars = 8000
    AllowWrite = $true
  }
}

foreach ($run in $runs) {
  Write-Host ""
  Write-Host ("Running DeepSeek {0} benchmark..." -f $run.Name)

  $argsList = @(
    "-m",
    "opencode_harness",
    "lab-compare",
    $run.Suite,
    "--presets",
    "deepseek",
    "--output-dir",
    (Join-Path $OutputDir $run.Name),
    "--comparison-output",
    $run.Comparison,
    "--max-steps",
    [string]$run.MaxSteps,
    "--context-chars",
    [string]$run.ContextChars
  )

  if ($run.AllowWrite) {
    $argsList += "--allow-write"
  }

  if ($IncludeMissingKey) {
    $argsList += "--include-missing-keys"
  }

  Write-Host "$Python $($argsList -join ' ')"
  & $Python @argsList

  Write-Host ("Comparison output: {0}" -f $run.Comparison)
  Write-Host ("Comparison JSON: {0}" -f ([System.IO.Path]::ChangeExtension($run.Comparison, ".json")))
}
