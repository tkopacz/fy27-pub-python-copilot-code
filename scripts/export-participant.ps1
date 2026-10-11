param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$Destination,
    [switch]$IncludePdf
)

$ErrorActionPreference = "Stop"
$SourceRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$TargetRoot = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Destination)
$TargetRoot = [IO.Path]::GetFullPath($TargetRoot)

function Assert-NoReparsePoint([string]$Path) {
    $Current = $Path
    while ($Current) {
        if (Test-Path -LiteralPath $Current) {
            $Item = Get-Item -LiteralPath $Current -Force
            if ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                throw "Links and junctions are not supported: $Current"
            }
        }
        $Current = Split-Path -Path $Current -Parent
    }
}

$SourcePrefix = $SourceRoot.TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
if ($TargetRoot.TrimEnd('\', '/') -eq $SourceRoot.TrimEnd('\', '/') -or
    $TargetRoot.StartsWith($SourcePrefix, [StringComparison]::OrdinalIgnoreCase)) {
    throw "Destination must be outside the source folder. Choose a new sibling folder."
}
if (Test-Path -LiteralPath $TargetRoot) {
    throw "Destination already exists; nothing was copied: $TargetRoot"
}
Assert-NoReparsePoint $TargetRoot
Assert-NoReparsePoint $SourceRoot

$Manifest = Join-Path $PSScriptRoot "participant-files.txt"
Assert-NoReparsePoint $Manifest
$Files = @(Get-Content -LiteralPath $Manifest | Where-Object { $_.Trim() })
if ($IncludePdf) {
    $Files += "lab.pdf"
}
if ($Files.Count -eq 0 -or (@($Files | Sort-Object -Unique)).Count -ne $Files.Count) {
    throw "The participant manifest must be nonempty and contain no duplicates."
}

# Validate the complete selection before creating the destination.
foreach ($Relative in $Files) {
    if ([IO.Path]::IsPathRooted($Relative) -or $Relative -match '[:/*?\[\]]' -or
        @($Relative.Split('\') | Where-Object { $_ -in @('', '.', '..') }).Count) {
        throw "Invalid relative path in participant manifest: $Relative"
    }
    $Source = Join-Path $SourceRoot $Relative
    Assert-NoReparsePoint $Source
    if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) {
        throw "Required participant file is missing: $Relative"
    }
}

New-Item -ItemType Directory -Path $TargetRoot | Out-Null
foreach ($Relative in $Files) {
    $Target = Join-Path $TargetRoot $Relative
    $Parent = Split-Path -Path $Target -Parent
    if (-not (Test-Path -LiteralPath $Parent)) {
        New-Item -ItemType Directory -Path $Parent -Force | Out-Null
    }
    Copy-Item -LiteralPath (Join-Path $SourceRoot $Relative) -Destination $Target -ErrorAction Stop
}

Write-Host "Copied $($Files.Count) files to $TargetRoot"
Write-Host "Open lab.md in the new folder. No Git history, environment or reports were copied."
