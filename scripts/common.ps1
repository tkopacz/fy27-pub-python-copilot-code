$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path $PSScriptRoot -Parent
$PythonExe = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

function Assert-LabEnvironment {
    if (-not (Test-Path $PythonExe)) {
        throw "Missing .venv. Run .\scripts\setup.ps1 first."
    }
}
