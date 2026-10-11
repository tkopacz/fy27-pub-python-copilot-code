param([Parameter(Mandatory = $true)][string]$RunDirectory)
$ErrorActionPreference = "Stop"
$Python = Join-Path (Get-Location).Path ".venv\Scripts\python.exe"
if (-not (Test-Path $Python -PathType Leaf)) {
    throw "Missing project .venv. Prepare the environment before running this skill."
}
New-Item -ItemType Directory -Force -Path $RunDirectory | Out-Null
$ReportPath = Join-Path $RunDirectory "evaluation.json"
$ExitPath = Join-Path $RunDirectory "metrics-exit.json"
if ((Test-Path $ReportPath) -or (Test-Path $ExitPath)) {
    throw "Evidence already exists. Use a new run directory."
}
$PreviousMode = $env:TRIAGE_MODE
$PreviousDotenv = $env:PYTHON_DOTENV_DISABLED
try {
    $env:TRIAGE_MODE = "demo"
    $env:PYTHON_DOTENV_DISABLED = "1"
    & $Python -m triage.evaluate --dataset starter\data\evaluation.json --output $ReportPath
    $Code = $LASTEXITCODE
}
finally {
    $env:TRIAGE_MODE = $PreviousMode
    $env:PYTHON_DOTENV_DISABLED = $PreviousDotenv
}
@{ command = "triage.evaluate"; exit_code = $Code } |
    ConvertTo-Json | Set-Content -LiteralPath $ExitPath -Encoding UTF8
exit $Code
