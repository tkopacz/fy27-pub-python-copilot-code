param(
    [ValidateSet("demo", "live")][string]$Mode = "demo",
    [ValidateRange(1024, 65535)][int]$Port = 5000
)
. "$PSScriptRoot\common.ps1"
Assert-LabEnvironment
$PreviousMode = $env:TRIAGE_MODE
Push-Location $ProjectRoot
try {
    $env:TRIAGE_MODE = $Mode
    & $PythonExe -m flask --app triage.app:create_app run --host 127.0.0.1 --port $Port --no-debugger --no-reload
    if ($LASTEXITCODE -ne 0) { throw "Application failed to start or stopped with an error." }
}
finally {
    $env:TRIAGE_MODE = $PreviousMode
    Pop-Location
}
