param(
    [string]$SubscriptionId = "6531b869-94be-4485-a471-e281a840e75e",
    [string]$ResourceGroup = "rgfy27-python-copilot",
    [string]$Location = "westeurope",
    [string]$AppName = "app-fy27-python-6531b869",
    [string]$PlanName = "asp-fy27-python-copilot",
    [string]$IdentityName = "id-fy27-python-github",
    [string]$Repository = "tkopacz/fy27-pub-python-copilot",
    [string]$FederatedSubject = ""
)
$ErrorActionPreference = "Stop"
if (-not $FederatedSubject) {
    $Metadata = gh api "repos/$Repository" `
        --jq '{owner:.owner.login,ownerId:.owner.id,name:.name,id:.id}'
    if ($LASTEXITCODE -ne 0) { throw "Could not resolve immutable GitHub repository IDs." }
    $Metadata = $Metadata | ConvertFrom-Json
    $FederatedSubject = "repo:$($Metadata.owner)@$($Metadata.ownerId)/$($Metadata.name)@$($Metadata.id):environment:azure-demo"
}
function Invoke-AzureJson {
    param([string[]]$Arguments)
    $Result = & az @Arguments --subscription $SubscriptionId --only-show-errors -o json
    if ($LASTEXITCODE -ne 0) { throw "Azure command failed: az $($Arguments[0..1] -join ' ')" }
    if ($Result) { return ($Result | ConvertFrom-Json) }
}
Invoke-AzureJson @("group", "create", "--name", $ResourceGroup, "--location", $Location) | Out-Null
Invoke-AzureJson @(
    "appservice", "plan", "create", "--name", $PlanName,
    "--resource-group", $ResourceGroup, "--location", $Location, "--sku", "B1", "--is-linux"
) | Out-Null
$App = Invoke-AzureJson @(
    "webapp", "create", "--name", $AppName, "--resource-group", $ResourceGroup,
    "--plan", $PlanName, "--runtime", "PYTHON:3.12", "--https-only", "true"
)
Invoke-AzureJson @(
    "webapp", "config", "set", "--name", $AppName, "--resource-group", $ResourceGroup,
    "--startup-file", "python -m gunicorn --bind 0.0.0.0:8000 --workers 2 --timeout 120 azure_demo_wsgi:app",
    "--min-tls-version", "1.2", "--ftps-state", "Disabled", "--always-on", "true"
) | Out-Null
Invoke-AzureJson @(
    "webapp", "log", "config", "--name", $AppName,
    "--resource-group", $ResourceGroup, "--docker-container-logging", "filesystem"
) | Out-Null
Invoke-AzureJson @(
    "webapp", "config", "appsettings", "set", "--name", $AppName,
    "--resource-group", $ResourceGroup, "--settings", "TRIAGE_MODE=demo",
    "SCM_DO_BUILD_DURING_DEPLOYMENT=false",
    "PYTHONPATH=/home/site/wwwroot/.python_packages/lib/site-packages"
) | Out-Null
$Identity = Invoke-AzureJson @(
    "identity", "create", "--name", $IdentityName, "--resource-group", $ResourceGroup
)
Invoke-AzureJson @(
    "identity", "federated-credential", "create", "--name", "github-azure-demo",
    "--identity-name", $IdentityName, "--resource-group", $ResourceGroup,
    "--issuer", "https://token.actions.githubusercontent.com",
    "--subject", $FederatedSubject,
    "--audiences", "api://AzureADTokenExchange"
) | Out-Null
$Roles = Invoke-AzureJson @(
    "role", "assignment", "list", "--assignee", $Identity.principalId,
    "--fill-principal-name", "false", "--scope", $App.id
)
if (-not ($Roles | Where-Object { $_.roleDefinitionName -eq "Website Contributor" })) {
    Invoke-AzureJson @(
        "role", "assignment", "create", "--assignee-object-id", $Identity.principalId,
        "--assignee-principal-type", "ServicePrincipal", "--role", "Website Contributor",
        "--scope", $App.id
    ) | Out-Null
}
$Account = Invoke-AzureJson @("account", "show")
[ordered]@{
    subscriptionId = $SubscriptionId
    tenantId = $Account.tenantId
    clientId = $Identity.clientId
    appName = $AppName
    url = "https://$($App.defaultHostName)"
    resourceGroup = $ResourceGroup
    federatedSubject = $FederatedSubject
} | ConvertTo-Json
