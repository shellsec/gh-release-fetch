# 打包 Windows Release：dist/release/gh-release-fetch-windows-<版本>.zip
# 用法:
#   powershell -ExecutionPolicy Bypass -File tools\pack_windows_release.ps1
#   powershell -ExecutionPolicy Bypass -File tools\pack_windows_release.ps1 -Version 20261114.3
#   powershell -ExecutionPolicy Bypass -File tools\pack_windows_release.ps1 -SkipBuild
param(
    [switch]$SkipBuild,
    [switch]$Gui,
    [string]$Version = "20261114.3"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if ($Version -cnotmatch '^[0-9]{8}\.[0-9]{1,6}$') { throw "Version must use YYYYMMDD.N format." }
$ver = $Version
$StageName = "gh-release-fetch-windows-$ver"
$OutDir = Join-Path $Root "dist\release"
$Stage = Join-Path $OutDir $StageName
$ZipPath = Join-Path $OutDir "$StageName.zip"

Write-Host "== Pack Windows release: $StageName ==" -ForegroundColor Cyan

if (-not $SkipBuild) {
    & (Join-Path $Root "tools\build_exe.ps1") -Gui:$Gui -Version $ver
}

$ExeDir = Join-Path $Root "dist\exe"
$exes = @("GHReleaseFetch.exe")
foreach ($name in $exes) {
    $p = Join-Path $ExeDir $name
    if (-not (Test-Path $p)) {
        throw "Missing $p — run tools\build_exe.ps1 first."
    }
}

$Built = Get-Content -Raw -LiteralPath (Join-Path $Root "build\pyinstaller\desktop-build.json") | ConvertFrom-Json
$ExePath = Join-Path $ExeDir "GHReleaseFetch.exe"
$ExeHash = (Get-FileHash -LiteralPath $ExePath).Hash
if ($Built.version -cne $ver -or $Built.sha256 -cne $ExeHash) { throw "EXE does not match the requested build version. Rebuild it first." }
if (Test-Path -LiteralPath $Stage) { throw "Output folder already exists: $Stage" }
New-Item -ItemType Directory -Force -Path $Stage | Out-Null

Write-Host "Copy GHReleaseFetch.exe..."
foreach ($name in $exes) {
    Copy-Item (Join-Path $ExeDir $name) (Join-Path $Stage $name) -Force
}
& {
    Compress-Archive -LiteralPath $Stage -DestinationPath $ZipPath -CompressionLevel Optimal -Force
    $ZipHash = (Get-FileHash -LiteralPath $ZipPath).Hash
    @("$($ExeHash.ToLowerInvariant())  GHReleaseFetch.exe", "$($ZipHash.ToLowerInvariant())  $StageName.zip") |
        Set-Content -LiteralPath (Join-Path $OutDir "SHA256SUMS-$ver.txt") -Encoding ascii
    Write-Host "Zip: $ZipPath"
    return
}
