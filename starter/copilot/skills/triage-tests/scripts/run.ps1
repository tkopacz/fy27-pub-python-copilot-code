param([Parameter(Mandatory = $true)][string]$RunDirectory)
$ErrorActionPreference = "Stop"
$Python = Join-Path (Get-Location).Path ".venv\Scripts\python.exe"
if (-not (Test-Path $Python -PathType Leaf)) {
    throw "Missing project .venv. Prepare the environment before running this skill."
}
New-Item -ItemType Directory -Force -Path $RunDirectory | Out-Null
$XmlPath = Join-Path $RunDirectory "tests.xml"
$ExitPath = Join-Path $RunDirectory "tests-exit.json"
if ((Test-Path $XmlPath) -or (Test-Path $ExitPath)) {
    throw "Evidence already exists. Use a new run directory."
}
& $Python -m pytest -q "--junitxml=$XmlPath"
$Code = $LASTEXITCODE
$Evidence = @{ command = "pytest"; exit_code = $Code }
if (Test-Path $XmlPath -PathType Leaf) {
    [xml]$Report = Get-Content -LiteralPath $XmlPath -Raw
    $Totals = @{ tests = 0; failures = 0; errors = 0; skipped = 0 }
    foreach ($Suite in $Report.SelectNodes("//testsuite")) {
        foreach ($Key in @("tests", "failures", "errors", "skipped")) {
            $Totals[$Key] += [int]$Suite.GetAttribute($Key)
        }
    }
    $Evidence.totals = $Totals
}
$Evidence |
    ConvertTo-Json | Set-Content -LiteralPath $ExitPath -Encoding UTF8
exit $Code
