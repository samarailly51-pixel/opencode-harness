param(
  [ValidateSet("smoke", "long-context", "repair", "all")]
  [string]$SuiteSet = "smoke",
  [string]$OutputDir = "eval-runs/deepseek-benchmark",
  [string]$DiagnosisDir = "model-labs/deepseek/reports",
  [string]$Python = "python",
  [switch]$IncludeMissingKey,
  [switch]$SkipDiagnosis
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
  $comparisonJson = [System.IO.Path]::ChangeExtension($run.Comparison, ".json")
  Write-Host ("Comparison JSON: {0}" -f $comparisonJson)

  if (-not $SkipDiagnosis) {
    $comparisonData = Get-Content $comparisonJson -Raw | ConvertFrom-Json
    $reportPaths = @($comparisonData.reports)
    if ($reportPaths.Count -gt 0) {
      $diagnosisOutput = Join-Path $DiagnosisDir ("{0}-diagnosis.md" -f $run.Name)
      New-Item -ItemType Directory -Force -Path (Split-Path $diagnosisOutput -Parent) | Out-Null
      $diagnoseArgs = @(
        "-m",
        "opencode_harness",
        "diagnose"
      )
      $diagnoseArgs += $reportPaths
      $diagnoseArgs += @(
        "--output",
        $diagnosisOutput
      )
      Write-Host "$Python $($diagnoseArgs -join ' ')"
      & $Python @diagnoseArgs
      Write-Host ("Diagnosis output: {0}" -f $diagnosisOutput)
    } else {
      Write-Host "No report paths found; skipping diagnosis."
    }
  }
}
