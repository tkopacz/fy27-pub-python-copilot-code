param([string[]]$PytestArgs = @())
. "$PSScriptRoot\common.ps1"
Assert-LabEnvironment
Push-Location $ProjectRoot
try {
    & $PythonExe -m pytest @PytestArgs
    $TestExitCode = $LASTEXITCODE
}
finally {
    Pop-Location
}
exit $TestExitCode
