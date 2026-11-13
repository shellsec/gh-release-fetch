# PyInstaller: dist/exe/*.exe
param([switch]$SkipInstall, [switch]$Gui, [string]$Version = "20261114.3")
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
if ($Version -cnotmatch '^[0-9]{8}\.[0-9]{1,6}$') { throw "Version must use YYYYMMDD.N format." }

Write-Host "== GH Release Fetch: build exe ==" -ForegroundColor Cyan

python --version 2>$null
if (-not $?) { throw "Python 3 not found." }

if (-not $SkipInstall) {
    python -m pip install -r requirements.txt pyinstaller --quiet
    if ($LASTEXITCODE -ne 0) { throw "Build dependencies could not be installed." }
}

$Dist = Join-Path $Root "dist\exe"
$Work = Join-Path $Root "build\pyinstaller"
New-Item -ItemType Directory -Force -Path $Dist, $Work | Out-Null
$VersionFile = Join-Path $Work "ghrf-version.txt"
Set-Content -LiteralPath $VersionFile -Value $Version -Encoding ascii

$HiddenCore = @(
    "--hidden-import", "tools.app_list",
    "--hidden-import", "tools.ghrf_runtime",
    "--hidden-import", "tools.apply_enabled_snapshot"
)
$IconName = "gh-release-fetch-gui.ico"
$Icon = Join-Path $Root "release\windows\$IconName"
$Common = @(
    "--noconfirm", "--clean",
    "--distpath", $Dist,
    "--workpath", $Work,
    "--specpath", $Work,
    "--paths", $Root,
    "--icon", $Icon
)

function Build-One($Name, $Entry, [string[]]$More = @()) {
    Write-Host ""
    Write-Host ">> $Name" -ForegroundColor Yellow
    python -m PyInstaller @Common @HiddenCore @More --onefile --name $Name $Entry
    if ($LASTEXITCODE -ne 0) { throw "pyinstaller failed: $Name" }
}

& {
    $Icons = Join-Path $Root "release\windows\gui-icons"
    $Data = @("--windowed", "--add-data", "$Icons;gui-icons", "--add-data", "$VersionFile;.")
    foreach ($directory in @("apps", "apps-mobile", "apps-tv", "apps-switch", "apps-ps4", "apps-ps5", "apps-vita", "apps-xbox", "apps-handheld", "VibeCodingToolsDown\dist\vibecoding", "tools\soft_page_check\history", "tools\soft_page_check\list")) {
        $Data += @("--add-data", "$(Join-Path $Root $directory);$directory")
    }
    foreach ($name in @("catalog.html", "tools\soft_page_check\soft_pages_urls.txt", "tools\soft_page_check\watch_tier_a_urls.txt", "tools\soft_page_check\423down_digest_urls.txt")) {
        if (Test-Path $name) {
            $parent = Split-Path -Parent $name
            if (-not $parent) { $parent = "." }
            $Data += @("--add-data", "$(Join-Path $Root $name);$parent")
        }
    }
    Build-One "GHReleaseFetch" "windows_gui.py" $Data
    $Hash = (Get-FileHash -LiteralPath (Join-Path $Dist "GHReleaseFetch.exe")).Hash
    @{version=$Version; sha256=$Hash} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $Work "desktop-build.json") -Encoding ascii
    return
}
