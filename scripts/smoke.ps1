param([ValidateRange(1024, 65535)][int]$Port = 5000)
$ErrorActionPreference = "Stop"
$BaseUrl = "http://127.0.0.1:$Port"
$Health = Invoke-RestMethod "$BaseUrl/health" -TimeoutSec 5
if ($Health.status -ne "ok") { throw "Health check failed." }
$HomeResponse = Invoke-WebRequest "$BaseUrl/" -UseBasicParsing -TimeoutSec 5
if ($HomeResponse.StatusCode -ne 200 -or $HomeResponse.Content -notmatch 'id="triage"') {
    throw "UI check failed."
}
$Body = @{ store_id = "store-001"; text = "Brak produktu." } | ConvertTo-Json
$Result = Invoke-RestMethod "$BaseUrl/api/triage" -Method Post -ContentType "application/json" -Body $Body -TimeoutSec 30
if ($Result.category -ne "product" -or $Result.priority -ne "P2" -or
    $Result.review_status -ne "draft_ready" -or $Result.jira_draft.project -ne "DEMO" -or
    $Result.mode -ne $Health.mode) {
    throw "Triage response does not satisfy the smoke contract."
}
Write-Host "PASS: GET /, GET /health, POST /api/triage. Mode: $($Result.mode). No Jira writes."
