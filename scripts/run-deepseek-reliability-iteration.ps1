param(
  [ValidateSet("smoke", "long-context", "repair", "all")]
  [string]$SuiteSet = "repair",
  [string]$OutputDir = "eval-runs/deepseek-benchmark",
  [string]$DiagnosisDir = "model-labs/deepseek/reports",
  [string]$Python = "python",
  [string]$BeforeLabel = "Published baseline",
  [string]$AfterLabel = "After repair verifier feedback",
  [switch]$SkipBenchmark
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

if (-not $SkipBenchmark -and [string]::IsNullOrWhiteSpace($env:DEEPSEEK_API_KEY)) {
  throw "DEEPSEEK_API_KEY is missing. Set it in this PowerShell session before running the DeepSeek reliability iteration."
}

$suiteNames = @()
if ($SuiteSet -eq "all") {
  $suiteNames = @("smoke", "long-context", "repair")
} else {
  $suiteNames = @($SuiteSet)
}

function Get-LatestReport {
  param([string]$SuiteName)

  $suiteDir = Join-Path $OutputDir $SuiteName
  $report = Get-ChildItem -Path $suiteDir -Recurse -Filter report.json -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

  if ($null -eq $report) {
    return $null
  }
  return $report.FullName
}

$beforeReports = [ordered]@{}
foreach ($suiteName in $suiteNames) {
  $beforeReports[$suiteName] = Get-LatestReport $suiteName
}

if (-not $SkipBenchmark) {
  & (Join-Path $PSScriptRoot "run-deepseek-benchmark.ps1") `
    -SuiteSet $SuiteSet `
    -OutputDir $OutputDir `
    -DiagnosisDir $DiagnosisDir `
    -Python $Python
}

$summaryPath = Join-Path $DiagnosisDir "reliability-iteration.md"
New-Item -ItemType Directory -Force -Path (Split-Path $summaryPath -Parent) | Out-Null

$summary = @(
  "# DeepSeek Reliability Iteration",
  "",
  "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz')",
  "",
  "| Suite | Before | After | Diagnosis Compare |",
  "| --- | --- | --- | --- |"
)

foreach ($suiteName in $suiteNames) {
  $before = $beforeReports[$suiteName]
  $after = Get-LatestReport $suiteName

  if ([string]::IsNullOrWhiteSpace($before)) {
    Write-Host ("No before report found for {0}; skipping diagnosis comparison." -f $suiteName)
    continue
  }
  if ([string]::IsNullOrWhiteSpace($after)) {
    Write-Host ("No after report found for {0}; skipping diagnosis comparison." -f $suiteName)
    continue
  }
  if ($before -eq $after) {
    Write-Host ("Before and after report are the same for {0}; skipping diagnosis comparison." -f $suiteName)
    continue
  }

  $compareOutput = Join-Path $DiagnosisDir ("{0}-before-after-diagnosis.md" -f $suiteName)
  $diagnoseArgs = @(
    "-m",
    "opencode_harness",
    "diagnose-compare",
    "--before",
    $before,
    "--after",
    $after,
    "--before-label",
    $BeforeLabel,
    "--after-label",
    $AfterLabel,
    "--output",
    $compareOutput
  )

  Write-Host ""
  Write-Host ("Comparing DeepSeek {0} reports..." -f $suiteName)
  Write-Host "$Python $($diagnoseArgs -join ' ')"
  & $Python @diagnoseArgs

  $relativeCompare = [System.IO.Path]::GetRelativePath((Resolve-Path $DiagnosisDir), (Resolve-Path $compareOutput)).Replace('\', '/')
  $summary += "| $suiteName | `$before` | `$after` | [$suiteName comparison]($relativeCompare) |"
}

$summary | Set-Content -Path $summaryPath -Encoding utf8

Write-Host ""
Write-Host "Reliability iteration summary:"
Write-Host "  $summaryPath"
