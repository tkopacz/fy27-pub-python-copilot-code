param([switch]$UseDeviceCode)
. "$PSScriptRoot\common.ps1"
Assert-LabEnvironment
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    throw "Azure CLI is required. Install it using your organization's approved process."
}

Push-Location $ProjectRoot
try {
    $TenantId = & $PythonExe -c "from dotenv import load_dotenv; import os, sys; load_dotenv(override=False); mode = os.environ.get('OPENAI_AUTH_MODE', 'api-key'); sys.exit('Set OPENAI_AUTH_MODE=azure-cli before login.') if mode != 'azure-cli' else None; print(os.environ.get('AZURE_TENANT_ID', '').strip())"
    if ($LASTEXITCODE -ne 0) { throw "Could not read tenant configuration." }
    $Arguments = @("login", "--output", "none")
    if ($TenantId) { $Arguments += @("--tenant", $TenantId) }
    if ($UseDeviceCode) { $Arguments += "--use-device-code" }
    & az @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Azure CLI login failed." }
    & $PythonExe -m triage.auth
    if ($LASTEXITCODE -ne 0) { throw "Azure token check failed. Check OPENAI_AUTH_MODE, tenant and scope." }
}
finally {
    Pop-Location
}
