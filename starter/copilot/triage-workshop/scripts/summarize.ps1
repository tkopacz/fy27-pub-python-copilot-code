param([Parameter(Mandatory = $true)][string]$RunDirectory)
$ErrorActionPreference = "Stop"
$Python = Join-Path (Get-Location).Path ".venv\Scripts\python.exe"
if (-not (Test-Path $Python -PathType Leaf)) {
    throw "Missing project .venv. Prepare the environment before summarizing."
}
& $Python (Join-Path $PSScriptRoot "summarize.py") --run-directory $RunDirectory
exit $LASTEXITCODE
