# 打包 Windows Release：dist/release/gh-release-fetch-windows-<版本>.zip
# 用法:
#   powershell -ExecutionPolicy Bypass -File tools\pack_windows_release.ps1
#   powershell -ExecutionPolicy Bypass -File tools\pack_windows_release.ps1 -Version 1.0.0
#   powershell -ExecutionPolicy Bypass -File tools\pack_windows_release.ps1 -SkipBuild
param(
    [switch]$SkipBuild,
    [switch]$Gui,
    [string]$Version = ""
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Get-ReleaseVersion {
    param([string]$Explicit)
    if ($Explicit) { if ($Explicit.Trim() -notmatch '^[a-zA-Z0-9][a-zA-Z0-9._-]*$') { throw "Invalid release version" }; return $Explicit.Trim() }
    $tag = git describe --tags --always 2>$null
    if ($LASTEXITCODE -eq 0 -and $tag) { return $tag -replace '[\\/:*?"<>|]', '-' }
    return (Get-Date -Format "yyyyMMdd")
}

$ver = Get-ReleaseVersion -Explicit $Version
$StageName = "gh-release-fetch-windows-$ver"
$OutDir = Join-Path $Root "dist\release"
$Stage = Join-Path $OutDir $StageName
$ZipPath = Join-Path $OutDir "$StageName.zip"

Write-Host "== Pack Windows release: $StageName ==" -ForegroundColor Cyan

if (-not $SkipBuild) {
    & (Join-Path $Root "tools\build_exe.ps1") -Gui:$Gui
}

$ExeDir = Join-Path $Root "dist\exe"
$exes = @("GHReleaseFetch.exe")
foreach ($name in $exes) {
    $p = Join-Path $ExeDir $name
    if (-not (Test-Path $p)) {
        throw "Missing $p — run tools\build_exe.ps1 first."
    }
}

if (Test-Path -LiteralPath $Stage) { throw "Output folder already exists: $Stage" }
New-Item -ItemType Directory -Force -Path $Stage | Out-Null

Write-Host "Copy GHReleaseFetch.exe..."
foreach ($name in $exes) {
    Copy-Item (Join-Path $ExeDir $name) (Join-Path $Stage $name) -Force
}
& {
    Compress-Archive -LiteralPath $Stage -DestinationPath $ZipPath -CompressionLevel Optimal -Force
    Write-Host "Zip: $ZipPath"
    return
}
