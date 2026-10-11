param(
    [ValidateSet("demo", "live")][string]$Mode = "demo",
    [string]$Dataset = "starter\data\evaluation.json",
    [string]$Output,
    [ValidateRange(0.0, 1.0)][double]$MinMacroF1
)
. "$PSScriptRoot\common.ps1"
Assert-LabEnvironment
$PreviousMode = $env:TRIAGE_MODE
Push-Location $ProjectRoot
try {
    $env:TRIAGE_MODE = $Mode
    $Arguments = @("-m", "triage.evaluate", "--dataset", $Dataset)
    if ($Output) { $Arguments += @("--output", $Output) }
    if ($PSBoundParameters.ContainsKey("MinMacroF1")) {
        $Arguments += @("--min-macro-f1", $MinMacroF1.ToString([System.Globalization.CultureInfo]::InvariantCulture))
    }
    & $PythonExe @Arguments
    $EvaluationExitCode = $LASTEXITCODE
}
finally {
    $env:TRIAGE_MODE = $PreviousMode
    Pop-Location
}
exit $EvaluationExitCode
