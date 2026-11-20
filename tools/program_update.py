"""Download and install a newer Windows desktop release."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from tempfile import mkdtemp

import requests

from tools.catalog_update import fetch
from tools.download_engine import download

VERSION = (Path(sys._MEIPASS) / "ghrf-version.txt").read_text(encoding="ascii").strip() if getattr(sys, "frozen", False) else "0.0"
REPOSITORY = "shellsec/gh-release-fetch"
EXE = "GHReleaseFetch.exe"
RELEASE = f"https://github.com/{REPOSITORY}/releases/download/"


def check():
    url = f"https://api.github.com/repos/{REPOSITORY}/releases/latest"
    for timeout in ((5, 8), (5, 15)):
        try:
            with requests.get(url, timeout=timeout) as response:
                response.raise_for_status()
                data = response.json()
            break
        except (requests.ConnectionError, requests.Timeout):
            continue
    else:
        raise ValueError("暂时无法连接 GitHub 检查程序更新，请稍后重试")
    tag = data.get("tag_name", "")
    if not re.fullmatch(r"\d{8}\.\d{1,6}", tag):
        return None
    if tuple(map(int, tag.split("."))) <= tuple(map(int, VERSION.split("."))):
        return None
    assets = {item["name"]: item for item in data.get("assets", [])}
    if not {EXE, f"SHA256SUMS-{tag}.txt"} <= assets.keys():
        raise ValueError("Release is missing the executable or checksum")
    digest = re.fullmatch(r"sha256:([a-f0-9]{64})", assets[EXE].get("digest") or "")
    return tag, (data.get("body") or "")[:1400], digest[1] if digest else None


def executable_checksum(tag, official_digest=None):
    if official_digest and re.fullmatch(r"[a-f0-9]{64}", official_digest):
        return official_digest
    url = f"{RELEASE}{tag}/SHA256SUMS-{tag}.txt"
    try:
        content = fetch(url, 8192).decode("ascii")
    except (requests.RequestException, ValueError) as exc:
        raise ValueError("无法从 GitHub 获取可信的程序校验值，请稍后重试") from exc
    matches = re.findall(r"(?mi)^([a-f0-9]{64})[ \t]+\*?GHReleaseFetch\.exe\r?$", content)
    if len(matches) != 1:
        raise ValueError("Missing or ambiguous executable checksum")
    return matches[0].lower()


def prepare(tag, executable, official_digest=None, *, on_status=None):
    folder = Path(mkdtemp(prefix=".ghrf-update-", dir=Path(executable).parent))
    try:
        digest = executable_checksum(tag, official_digest)
        download(f"{RELEASE}{tag}/{EXE}", folder / EXE, digest=digest,
                 report=lambda _: None, on_status=on_status)
        return folder
    except Exception:
        from shutil import rmtree
        rmtree(folder, ignore_errors=True)
        raise


def launch(folder, executable):
    (folder / "update.json").write_text(json.dumps({"pid": os.getpid(), "exe": str(executable)}), encoding="ascii")
    script = folder / "install.ps1"
    script.write_text(INSTALL_SCRIPT, encoding="ascii")
    powershell = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32/WindowsPowerShell/v1.0/powershell.exe"
    subprocess.Popen([str(powershell), "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                      "-File", str(script)], creationflags=subprocess.CREATE_NO_WINDOW)


INSTALL_SCRIPT = r"""
$ErrorActionPreference = 'Stop'
$job = Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot 'update.json') | ConvertFrom-Json
$exe = [string]$job.exe
$replacement = Join-Path $PSScriptRoot 'GHReleaseFetch.exe'
$backup = Join-Path $PSScriptRoot 'previous.exe'
try {
    $process = Get-Process -Id $job.pid -ErrorAction SilentlyContinue
    if ($process -and !$process.WaitForExit(60000)) { throw 'The app did not exit in time.' }
    for ($attempt = 0; ; $attempt++) {
        try {
            [IO.File]::Replace($replacement, $exe, $backup)
            break
        } catch [IO.IOException] {
            if ($attempt -ge 30) { throw }
            Start-Sleep -Milliseconds 300
        }
    }
    $env:PYINSTALLER_RESET_ENVIRONMENT = '1'
    try { Start-Process -FilePath $exe -WorkingDirectory (Split-Path -Parent $exe) -WindowStyle Normal }
    catch {
        [IO.File]::Replace($backup, $exe, $null)
        throw
    }
} catch {
    $_ | Out-File -LiteralPath (Join-Path $PSScriptRoot 'error.txt') -Encoding utf8
    Add-Type -AssemblyName System.Windows.Forms
    [void][Windows.Forms.MessageBox]::Show($_.Exception.Message, 'GH Release Fetch - Update failed')
    exit 1
}
Remove-Item -LiteralPath $backup,(Join-Path $PSScriptRoot 'update.json') -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath $PSCommandPath -Force -ErrorAction SilentlyContinue
[IO.Directory]::Delete($PSScriptRoot)
"""
