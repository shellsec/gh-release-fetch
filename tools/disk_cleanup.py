"""Windows cleanup for known locations. Adapted from WindowsBatchScriptManager (Apache-2.0)."""
from dataclasses import dataclass, field
import os
from pathlib import Path
import stat
import base64
import ctypes
import shutil
import json
import subprocess
from datetime import datetime


@dataclass
class Cache:
    name: str
    path: Path
    files: list
    skipped: int = 0
    kind: str = "cache"
    restore_id: int | None = None
    issues: list[str] = field(default_factory=list)

    @property
    def size(self):
        return sum(info.st_size for _, info in self.files)


def fixed_drives():
    import ctypes
    from ctypes import wintypes
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetDriveTypeW.argtypes = [wintypes.LPCWSTR]
    mask = kernel.GetLogicalDrives()
    return [Path(f"{chr(65 + n)}:\\") for n in range(26)
            if mask & (1 << n) and kernel.GetDriveTypeW(f"{chr(65 + n)}:\\") == 3]


def plain_path(path):
    for part in (*reversed(path.parents), path):
        info = part.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            return False
        if not stat.S_ISDIR(info.st_mode):
            return False
    return True


def cache_roots():
    local = Path(os.environ["LOCALAPPDATA"])
    profile = Path(os.environ["USERPROFILE"])
    roots = [local]
    for drive in fixed_drives():
        # Only the current user's standard profile layout is recognized.
        roots.append(drive / "Users" / profile.name / "AppData" / "Local")
    seen = set()
    for root in roots:
        identity = os.path.normcase(str(root))
        if identity in seen:
            continue
        seen.add(identity)
        try:
            if not plain_path(root):
                continue
            for name, relative in (
                ("DirectX", "D3DSCache"),
                ("NVIDIA", "NVIDIA/DXCache"),
                ("NVIDIA", "NVIDIA/GLCache"),
                ("AMD", "AMD/DxCache"),
                ("AMD", "AMD/GLCache"),
            ):
                yield name, root / relative
            for browser, relative in (
                ("Chrome", "Google/Chrome/User Data"),
                ("Edge", "Microsoft/Edge/User Data"),
            ):
                base = root / relative
                if not base.is_dir() or not plain_path(base):
                    continue
                for child in base.iterdir():
                    if child.name != "Default" and not child.name.startswith("Profile "):
                        continue
                    for folder in ("Cache", "Code Cache", "GPUCache"):
                        yield browser, child / folder
            firefox = root / "Mozilla/Firefox/Profiles"
            if firefox.is_dir() and plain_path(firefox):
                for child in firefox.iterdir():
                    yield "Firefox", child / "cache2"
        except OSError:
            continue


def scan_cache(name, root, *, kind="cache", excluded=(), protected=()):
    cache = Cache(name, root, [], kind=kind)
    excluded = {os.path.normcase(str(Path(path).absolute())) for path in excluded}
    pending = [root]
    while pending:
        directory = pending.pop()
        try:
            if any(directory == path or path in directory.parents for path in protected):
                cache.skipped += 1
                cache.issues.append(f"{directory}: protected path")
                continue
            if not plain_path(directory):
                cache.skipped += 1
                cache.issues.append(f"{directory}: reparse point or non-directory")
                continue
            with os.scandir(directory) as entries:
                for entry in entries:
                    try:
                        info = Path(entry.path).lstat()
                        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                            continue
                        if stat.S_ISDIR(info.st_mode):
                            pending.append(Path(entry.path))
                        elif stat.S_ISREG(info.st_mode):
                            if os.path.normcase(str(Path(entry.path).absolute())) in excluded:
                                continue
                            if kind == "temp" and not entry.name.lower().endswith((".tmp", ".temp")):
                                continue
                            if kind == "thumbnails" and not (entry.name.lower().startswith("thumbcache_") and entry.name.lower().endswith(".db")):
                                continue
                            if kind == "logs" and not entry.name.lower().endswith((".log", ".log.bak", ".log.gz")):
                                continue
                            if kind == "dumps" and not entry.name.lower().endswith(".dmp"):
                                continue
                            if kind == "prefetch" and not entry.name.lower().endswith(".pf"):
                                continue
                            cache.files.append((Path(entry.path), info))
                    except OSError as exc:
                        cache.skipped += 1
                        cache.issues.append(f"{entry.path}: {exc}")
        except FileNotFoundError:
            continue
        except OSError as exc:
            cache.skipped += 1
            cache.issues.append(f"{directory}: {exc}")
    return cache


def scan_restore_points():
    windows = Path(os.environ.get("SystemRoot") or r"C:\Windows")
    powershell = windows / "System32/WindowsPowerShell/v1.0/powershell.exe"
    command = (
        "[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false);"
        "$ErrorActionPreference='Stop';"
        "@(Get-CimInstance -Namespace root/default -ClassName SystemRestore | "
        "Select-Object SequenceNumber,Description,CreationTime) | ConvertTo-Json -Compress"
    )
    result = subprocess.run(
        [str(powershell), "-NoProfile", "-NonInteractive", "-Command", command],
        capture_output=True, timeout=25, creationflags=subprocess.CREATE_NO_WINDOW,
    )
    if result.returncode:
        raise OSError(result.stderr.decode("utf-8", errors="replace").strip())
    records = json.loads(result.stdout.decode("utf-8-sig") or "[]")
    if isinstance(records, dict):
        records = [records]
    return [
        Cache(f"{record['SequenceNumber']} — {record['Description']} — {record['CreationTime']}",
              windows, [], kind="restore", restore_id=int(record["SequenceNumber"]))
        for record in records
    ]


def scan(profile, task_log, *, quick=False, active_log=False, protected=(), temp_protected=()):
    windows = Path(os.environ.get("SystemRoot") or r"C:\Windows")
    local = Path(os.environ["LOCALAPPDATA"])
    results = []
    targets = [(name, path, "cache") for name, path in cache_roots()]
    targets.extend([
        ("User temporary files", local / "Temp", "temp"),
        ("System temporary files", windows / "Temp", "temp"),
        ("Thumbnail cache", local / "Microsoft/Windows/Explorer", "thumbnails"),
        ("GH Release Fetch crash dumps", profile / "CrashDumps", "dumps"),
    ])
    fixed = {path.drive.upper() for path in fixed_drives()}
    for name, path, kind in targets:
        if path.drive.upper() not in fixed or quick and path.drive.upper() != "C:":
            continue
        guard = (*protected, *temp_protected) if kind == "temp" else protected
        cache = scan_cache(name, path, kind=kind, protected=guard)
        if cache.files or cache.skipped:
            results.append(cache)
    if task_log.drive.upper() in fixed and (not quick or task_log.drive.upper() == "C:"):
        try:
            info = task_log.lstat()
            if plain_path(task_log.parent) and stat.S_ISREG(info.st_mode) and not getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                results.append(Cache("GH Release Fetch task log", task_log,
                                     [] if active_log else [(task_log, info)],
                                     skipped=int(active_log), kind="logs"))
        except FileNotFoundError:
            pass
        except OSError as exc:
            results.append(Cache("GH Release Fetch task log", task_log, [], skipped=1, kind="logs", issues=[str(exc)]))
    if not quick:
        windows = Path(os.environ.get("SystemRoot") or r"C:\Windows")
        hibernation = Path(windows.anchor) / "hiberfil.sys"
        try:
            if plain_path(hibernation.parent):
                info = hibernation.lstat()
                if stat.S_ISREG(info.st_mode) and not getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                    results.append(Cache("Hibernation", hibernation, [(hibernation, info)], kind="hibernate"))
        except FileNotFoundError:
            pass
        except OSError as exc:
            results.append(Cache("Hibernation", hibernation, [], skipped=1,
                                 kind="hibernate", issues=[str(exc)]))
        prefetch = scan_cache("Prefetch", windows / "Prefetch", kind="prefetch", protected=protected)
        if prefetch.files or prefetch.skipped:
            results.append(prefetch)
        try:
            results.extend(scan_restore_points())
        except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
            results.append(Cache(str(exc), windows, [], kind="notice"))
    return results


def system_command(name):
    return str(Path(os.environ.get("SystemRoot") or r"C:\Windows") / "System32" / name)


def run_command(args, *, timeout=60):
    result = subprocess.run(args, capture_output=True, timeout=timeout, creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:
        message = (result.stderr or result.stdout).decode("oem", errors="replace").strip()
        raise OSError(message or f"Windows command failed ({result.returncode}).")
    return result.stdout


def run_admin(script):
    powershell = system_command("WindowsPowerShell/v1.0/powershell.exe")
    if not ctypes.windll.shell32.IsUserAnAdmin():
        payload = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
        script = (
            "$ErrorActionPreference='Stop';"
            "$p=Start-Process -FilePath (Join-Path $PSHOME 'powershell.exe') -Verb RunAs -WindowStyle Hidden "
            f"-ArgumentList '-NoProfile -NonInteractive -EncodedCommand {payload}' -Wait -PassThru;"
            "exit $p.ExitCode"
        )
    encoded = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
    run_command([powershell, "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded], timeout=None)


def remove(cache, note=lambda message: None, *, protected=()):
    if cache.kind == "notice":
        return 0, 0, 1
    if cache.kind == "hibernate":
        expected = Path(Path(system_command("powercfg.exe")).anchor) / "hiberfil.sys"
        if cache.path != expected:
            raise ValueError("Invalid hibernation file path.")
        run_admin("& (Join-Path $env:SystemRoot 'System32/powercfg.exe') /hibernate off; exit $LASTEXITCODE")
        if cache.path.exists():
            raise OSError("Windows has not yet removed hiberfil.sys.")
        return 1, cache.size, 0
    if cache.kind == "restore":
        point = cache.restore_id
        if type(point) is not int or not 0 < point <= 0xffffffff:
            raise ValueError("Invalid restore point ID.")
        run_admin("$ErrorActionPreference='Stop';"
                  'Add-Type -MemberDefinition \'[DllImport("SrClient.dll")] public static extern uint SRRemoveRestorePoint(uint id);\' -Name Restore -Namespace Cleanup;'
                  f"if ([Cleanup.Restore]::SRRemoveRestorePoint({point}) -ne 0) {{ exit 1 }}")
        return 1, 0, 0
    browser = {"Chrome": "chrome.exe", "Edge": "msedge.exe", "Firefox": "firefox.exe"}.get(cache.name)
    if browser:
        try:
            processes = run_command([system_command("tasklist.exe"), "/FI", f"IMAGENAME eq {browser}", "/FO", "CSV", "/NH"])
        except (OSError, subprocess.TimeoutExpired) as exc:
            note(f"Could not check browser process: {exc}")
            return 0, 0, len(cache.files) + cache.skipped
        if f'"{browser}"'.encode() in processes.lower():
            note(f"{browser} is running; cache skipped.")
            return 0, 0, len(cache.files) + cache.skipped
    removed = size = 0
    skipped = cache.skipped
    for path, before in cache.files:
        try:
            if any(path == root or root in path.parents for root in protected):
                skipped += 1
                note(f"{path}: protected by an active download")
                continue
            if not plain_path(path.parent):
                skipped += 1
                note(f"{path}: parent is a reparse point or non-directory")
                continue
            current = path.lstat()
            if (not stat.S_ISREG(current.st_mode)
                    or getattr(current, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
                    or (current.st_ino, current.st_size, current.st_mtime_ns) !=
                    (before.st_ino, before.st_size, before.st_mtime_ns)):
                skipped += 1
                note(f"{path}: file changed after scanning or is a reparse point")
                continue
            path.unlink()
            removed += 1
            size += before.st_size
        except OSError as exc:
            skipped += 1
            note(f"{path}: {exc}")
    return removed, size, skipped


def clean(targets, report_path, *, quick=False, active_log=False, protected=()):
    report_path.parent.mkdir(parents=True, exist_ok=True)
    totals = [0, 0, 0]
    with report_path.open("a", encoding="utf-8") as report:
        print(f"\n[{datetime.now().isoformat(timespec='seconds')}] {'C: cleanup' if quick else 'Checked items'}", file=report, flush=True)
        before = shutil.disk_usage("C:/").free if quick else None
        for cache in targets:
            def note(message):
                print(f"{cache.name} | {cache.path} | {message}", file=report)

            for issue in cache.issues:
                note(issue)
            try:
                if cache.kind == "logs" and active_log:
                    note("Download log is in use.")
                    result = (0, 0, len(cache.files) + cache.skipped)
                else:
                    result = remove(cache, note, protected=protected)
            except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
                note(exc)
                result = (0, 0, max(1, len(cache.files)))
            print(f"{cache.name} | {cache.path} | removed={result[0]}, bytes={result[1]}, skipped={result[2]}", file=report, flush=True)
            totals = [left + right for left, right in zip(totals, result)]
        if quick:
            try:
                run_command([system_command("ipconfig.exe"), "/flushdns"])
                print("DNS cache flushed.", file=report)
            except (OSError, subprocess.TimeoutExpired) as exc:
                totals[2] += 1
                print(f"DNS cache: {exc}", file=report)
        change = shutil.disk_usage("C:/").free - before if before is not None else None
        print(f"Removed={totals[0]}, bytes={totals[1]}, skipped={totals[2]}, C: free space change={change}", file=report)
    return *totals, change
