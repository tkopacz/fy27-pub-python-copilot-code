param([switch]$WithLLM)
. "$PSScriptRoot\common.ps1"

Push-Location $ProjectRoot
try {
    python -c "import sys; assert sys.version_info >= (3, 11), 'Python 3.11+ required'"
    if ($LASTEXITCODE -ne 0) { throw "Python 3.11+ is required." }
    if (-not (Test-Path $PythonExe)) {
        python -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw "Could not create .venv." }
    }
    $Requirements = if ($WithLLM) { "requirements-llm.txt" } else { "requirements.txt" }
    Write-Host "Checking packages using the existing pip registry/proxy configuration."
    & $PythonExe -m pip install --dry-run -r $Requirements
    if ($LASTEXITCODE -ne 0) {
        throw "Dependencies unavailable. Check the corporate pip registry/proxy; do not switch to a public registry."
    }
    & $PythonExe -m pip install -r $Requirements
    if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }
    & $PythonExe -m pip check
    if ($LASTEXITCODE -ne 0) { throw "Dependency consistency check failed." }
    Write-Host "Ready. Run .\scripts\test.ps1 (one intentional failure), then .\scripts\run.ps1."
}
finally {
    Pop-Location
}
