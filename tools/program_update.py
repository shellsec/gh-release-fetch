"""Download and install a newer Windows desktop release."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from tempfile import mkdtemp

import requests

from tools.download_engine import download_url

VERSION = (Path(sys._MEIPASS) / "ghrf-version.txt").read_text(encoding="ascii").strip() if getattr(sys, "frozen", False) else "0.0"
REPOSITORY = "shellsec/gh-release-fetch"
EXE = "GHReleaseFetch.exe"
RELEASE = f"https://github.com/{REPOSITORY}/releases/download/"


def check():
    with requests.get(f"https://api.github.com/repos/{REPOSITORY}/releases/latest", timeout=(5, 10)) as response:
        response.raise_for_status()
        data = response.json()
    tag = data.get("tag_name", "")
    if not re.fullmatch(r"\d{8}\.\d{1,6}", tag):
        return None
    if tuple(map(int, tag.split("."))) <= tuple(map(int, VERSION.split("."))):
        return None
    names = {item["name"] for item in data.get("assets", [])}
    if not {EXE, f"SHA256SUMS-{tag}.txt"} <= names:
        raise ValueError("Release is missing the executable or checksum")
    return tag, (data.get("body") or "")[:1400]


def prepare(tag, executable):
    folder = Path(mkdtemp(prefix=".ghrf-update-", dir=Path(executable).parent))
    try:
        with requests.get(f"{RELEASE}{tag}/SHA256SUMS-{tag}.txt", timeout=(5, 15), stream=True) as response:
            response.raise_for_status()
            content = response.raw.read(8193)
        if len(content) > 8192:
            raise ValueError("Checksum file exceeds size limit")
        matches = re.findall(r"(?mi)^([a-f0-9]{64})[ \t]+\*?GHReleaseFetch\.exe\r?$", content.decode("ascii"))
        if len(matches) != 1:
            raise ValueError("Missing or ambiguous executable checksum")
        download_url(f"{RELEASE}{tag}/{EXE}", folder / EXE, digest=matches[0].lower(), report=lambda _: None)
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
