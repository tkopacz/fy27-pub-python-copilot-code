param(
    [Parameter(Mandatory)][string]$AppName,
    [Parameter(Mandatory)][string]$SubscriptionId,
    [Parameter(Mandatory)][string]$Commit,
    [string]$ResourceGroup = "rgfy27-python-copilot",
    [string]$Python = "python"
)
$ErrorActionPreference = "Stop"
$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$Build = Join-Path $Root "reports\azure-demo\$Commit"
$Dependencies = Join-Path $Build "dependencies"
$Source = Join-Path $Build "source"
$SourceArchive = Join-Path $Build "source.zip"
$Archive = Join-Path $Build "app.zip"
$Evidence = Join-Path $Build "smoke.json"
if ($Commit -notmatch '^[a-f0-9]{40}$') { throw "Commit must be a full Git SHA." }
if (Test-Path $Dependencies) { throw "Use a fresh build directory: $Build" }
New-Item -ItemType Directory -Path $Build -Force | Out-Null
Push-Location $Root
try {
    git archive --format=zip "--output=$SourceArchive" $Commit `
        triage requirements.txt requirements-azure-demo.txt scripts/demo/wsgi.py
    if ($LASTEXITCODE -ne 0) { throw "Could not export the approved Git snapshot." }
    Expand-Archive -LiteralPath $SourceArchive -DestinationPath $Source
    $InstallArgs = @(
        "-m", "pip", "install", "--disable-pip-version-check",
        "--platform", "manylinux2014_x86_64", "--python-version", "3.12",
        "--only-binary=:all:", "--target", $Dependencies,
        "-r", (Join-Path $Source "requirements-azure-demo.txt")
    )
    & $Python @InstallArgs --dry-run
    if ($LASTEXITCODE -ne 0) { throw "Linux packages unavailable through configured corporate pip/proxy." }
    & $Python @InstallArgs
    if ($LASTEXITCODE -ne 0) { throw "Linux dependency build failed." }
    & $Python "scripts\demo\azure_demo.py" package `
        --root $Source --dependencies $Dependencies --output $Archive --commit $Commit
    if ($LASTEXITCODE -ne 0) { throw "Packaging failed." }
    az webapp deploy --subscription $SubscriptionId `
        --resource-group $ResourceGroup --name $AppName `
        --src-path $Archive --type zip --track-status false --only-show-errors -o none
    if ($LASTEXITCODE -ne 0) { throw "Azure ZIP deployment failed." }
    $HostName = az webapp show --subscription $SubscriptionId `
        --resource-group $ResourceGroup --name $AppName `
        --query defaultHostName -o tsv --only-show-errors
    if ($LASTEXITCODE -ne 0 -or -not $HostName) { throw "Could not resolve App Service URL." }
    & $Python "scripts\demo\azure_demo.py" smoke `
        --url "https://$HostName" --commit $Commit --output $Evidence
    if ($LASTEXITCODE -ne 0) { throw "Deployment smoke checks failed." }
}
finally {
    Pop-Location
}
