param(
  [string]$Suite = "model-labs/deepseek/deepseek-v4-suite.json",
  [string]$OutputDir = "eval-runs/real-provider-benchmark",
  [string]$ComparisonOutput = "benchmarks/real-provider-comparison/provider-comparison.md",
  [string[]]$Presets = @("deepseek", "qwen", "openai", "claude"),
  [int]$MaxSteps = 8,
  [int]$ContextChars = 8000,
  [string]$Python = "python",
  [switch]$IncludeMissingKeys
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

$required = [ordered]@{
  deepseek = "DEEPSEEK_API_KEY"
  qwen = "DASHSCOPE_API_KEY"
  openai = "OPENAI_API_KEY"
  claude = "ANTHROPIC_API_KEY"
  "local-openai" = "LOCAL_MODEL_API_KEY"
  vllm = "VLLM_API_KEY"
  sglang = "SGLANG_API_KEY"
  ollama = "OLLAMA_API_KEY"
}

Write-Host "Provider credential status:"
foreach ($preset in $Presets) {
  if ($required.Contains($preset)) {
    $envName = $required[$preset]
    $value = [Environment]::GetEnvironmentVariable($envName)
    $status = if ([string]::IsNullOrWhiteSpace($value)) { "missing" } else { "present" }
    Write-Host ("  {0}: {1} ({2})" -f $preset, $status, $envName)
  }
}

$argsList = @(
  "-m",
  "opencode_harness",
  "lab-compare",
  $Suite,
  "--presets"
) + $Presets + @(
  "--output-dir",
  $OutputDir,
  "--comparison-output",
  $ComparisonOutput,
  "--max-steps",
  [string]$MaxSteps,
  "--context-chars",
  [string]$ContextChars
)

if ($IncludeMissingKeys) {
  $argsList += "--include-missing-keys"
}

Write-Host ""
Write-Host "Running provider benchmark:"
Write-Host "$Python $($argsList -join ' ')"
& $Python @argsList

Write-Host ""
Write-Host "Comparison output:"
Write-Host "  $ComparisonOutput"
Write-Host "  $([System.IO.Path]::ChangeExtension($ComparisonOutput, '.json'))"
