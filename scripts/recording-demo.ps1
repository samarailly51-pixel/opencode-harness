param(
  [string]$OutputDir = "eval-runs/recording-demo",
  [string]$Python = "python"
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

$OutputPath = New-Item -ItemType Directory -Force -Path $OutputDir

function Invoke-RecordedStep {
  param(
    [string]$Name,
    [string[]]$Command,
    [string]$Transcript
  )

  Write-Host ""
  Write-Host "==> $Name"
  Write-Host ($Command -join " ")
  & $Command[0] @($Command[1..($Command.Length - 1)]) 2>&1 | Tee-Object -FilePath (Join-Path $OutputPath $Transcript)
}

Invoke-RecordedStep `
  -Name "Version" `
  -Command @($Python, "-m", "opencode_harness", "version") `
  -Transcript "01-version.txt"

Invoke-RecordedStep `
  -Name "Mock eval" `
  -Command @(
    $Python,
    "-m",
    "opencode_harness",
    "eval",
    "examples/mock-suite.json",
    "--preset",
    "mock",
    "--max-steps",
    "2",
    "--context-chars",
    "1000",
    "--output-dir",
    $OutputPath.FullName
  ) `
  -Transcript "02-eval.txt"

$Trace = Get-ChildItem $OutputPath -Recurse -Filter "inspect-repo.jsonl" |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1

if (-not $Trace) {
  throw "Could not find inspect-repo.jsonl under $($OutputPath.FullName)"
}

Invoke-RecordedStep `
  -Name "Trace replay" `
  -Command @($Python, "-m", "opencode_harness", "replay", $Trace.FullName) `
  -Transcript "03-replay.txt"

Invoke-RecordedStep `
  -Name "Terminal trace viewer" `
  -Command @($Python, "-m", "opencode_harness", "tui", $Trace.FullName, "--width", "88") `
  -Transcript "04-tui.txt"

Invoke-RecordedStep `
  -Name "HTML trace" `
  -Command @(
    $Python,
    "-m",
    "opencode_harness",
    "trace-html",
    $Trace.FullName,
    "--output",
    (Join-Path $OutputPath "latest-trace.html")
  ) `
  -Transcript "05-trace-html.txt"

Invoke-RecordedStep `
  -Name "Eval dashboard" `
  -Command @(
    $Python,
    "-m",
    "opencode_harness",
    "dashboard",
    $OutputPath.FullName,
    "--output",
    (Join-Path $OutputPath "dashboard.html")
  ) `
  -Transcript "06-dashboard.txt"

Write-Host ""
Write-Host "Recording demo artifacts:"
Write-Host "  Output dir: $($OutputPath.FullName)"
Write-Host "  Trace:      $($Trace.FullName)"
Write-Host "  Trace HTML: $((Join-Path $OutputPath 'latest-trace.html'))"
Write-Host "  Dashboard:  $((Join-Path $OutputPath 'dashboard.html'))"
Write-Host ""
Write-Host "Suggested browser shots:"
Write-Host "  https://samarailly51-pixel.github.io/opencode-harness/"
Write-Host "  $((Resolve-Path (Join-Path $OutputPath 'latest-trace.html')).Path)"
Write-Host "  $((Resolve-Path (Join-Path $OutputPath 'dashboard.html')).Path)"
