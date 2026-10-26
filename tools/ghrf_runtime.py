# -*- coding: utf-8 -*-
"""仓库根目录与 exe / .py 双模式调用解析（PyInstaller frozen）。"""
from __future__ import annotations

import os
import shlex
import sys


def console_image_paths() -> list[str]:
    """Resolve attached process images; PyInstaller onefile has two matching images."""
    import ctypes
    from ctypes import wintypes

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetConsoleProcessList.argtypes = [ctypes.POINTER(wintypes.DWORD), wintypes.DWORD]
    kernel.GetConsoleProcessList.restype = wintypes.DWORD
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
    kernel.QueryFullProcessImageNameW.restype = wintypes.BOOL
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    processes = (wintypes.DWORD * 64)()
    count = kernel.GetConsoleProcessList(processes, len(processes))
    if not count or count > len(processes):
        return []
    paths = []
    for process_id in processes[:count]:
        handle = kernel.OpenProcess(0x1000, False, process_id)
        if not handle:
            return []
        try:
            buffer = ctypes.create_unicode_buffer(32768)
            size = wintypes.DWORD(len(buffer))
            if not kernel.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size)):
                return []
            paths.append(buffer.value)
        finally:
            kernel.CloseHandle(handle)
    return paths


def owns_console_window() -> bool:
    """True only for a frozen Windows application that owns its console."""
    if os.name != "nt" or not is_frozen() or not sys.stdin or not sys.stdin.isatty():
        return False
    if os.environ.get("GH_RELEASE_FETCH_NO_PAUSE") == "1":
        return False
    try:
        paths = console_image_paths()
        executable = os.path.normcase(os.path.abspath(sys.executable))
        return bool(paths) and all(os.path.normcase(os.path.abspath(path)) == executable for path in paths)
    except (AttributeError, OSError):
        return False


def run_cli(main) -> int:
    """Preserve diagnostics on double-click without blocking shell/automation callers."""
    if os.name == "nt" and is_frozen():
        for stream in (sys.stdout, sys.stderr):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (AttributeError, OSError):
                pass
    own_console = owns_console_window()
    try:
        code = main() or 0
    except SystemExit as error:
        code = error.code if isinstance(error.code, int) else (1 if error.code else 0)
    except KeyboardInterrupt:
        print("\n已取消。", file=sys.stderr)
        return 130
    except Exception:
        import traceback
        from pathlib import Path
        import tempfile

        details = traceback.format_exc()
        print(details, file=sys.stderr)
        for folder in (Path(repo_root()), Path(tempfile.gettempdir()) / "gh-release-fetch"):
            try:
                folder.mkdir(parents=True, exist_ok=True)
                log_path = folder / "startup_error.log"
                with log_path.open("a", encoding="utf-8") as log:
                    log.write(details + "\n")
                print("错误详情已保存：%s" % log_path, file=sys.stderr)
                break
            except OSError:
                continue
        code = 1
    if own_console and code:
        try:
            input("\n运行未完成，请查看上方原因。按回车关闭窗口…")
        except (EOFError, KeyboardInterrupt):
            pass
    return code


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def repo_root(from_file: str | None = None) -> str:
    """配置与 JSON 所在目录：frozen 时为 exe 同目录，否则为仓库根。"""
    if is_frozen():
        return os.path.dirname(os.path.abspath(sys.executable))
    if from_file:
        path = os.path.abspath(from_file)
        norm = path.replace("\\", "/")
        if os.path.basename(path).startswith("run_saved") or norm.endswith("/tools/run_saved_apps.py"):
            return os.path.dirname(os.path.dirname(path))
        if norm.endswith("/tools/soft_page_check/search_pages.py"):
            return os.path.dirname(os.path.dirname(os.path.dirname(path)))
        return os.path.dirname(path)
    return os.path.dirname(os.path.abspath(sys.argv[0]))


def soft_page_check_dir(from_file: str | None = None) -> str:
    return os.path.join(repo_root(from_file), "tools", "soft_page_check")


def prompt_cli_line(
    usage_lines: list[str],
    prompt: str,
    *,
    allow_empty: bool = False,
) -> str | None:
    """无命令行参数时展示用法并读一行；取消或空输入返回 None。"""
    for line in usage_lines:
        print(line)
    print()
    try:
        text = input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print("\n已取消。")
        return None
    if not text:
        if allow_empty:
            return ""
        print("未输入，已退出。")
        return None
    return text


def argv_from_prompt(
    usage_lines: list[str],
    prompt: str,
) -> bool:
    """
    若 sys.argv 仅有程序名，则提示输入并 shlex 拆入 sys.argv。
    返回 False 表示用户取消或空输入（调用方应 exit 0）。
    """
    if len(sys.argv) > 1:
        return True
    text = prompt_cli_line(usage_lines, prompt)
    if text is None:
        return False
    sys.argv[1:] = shlex.split(text, posix=(os.name != "nt"))
    return True


def resolve_auto_update_argv(root: str, extra: list[str] | None = None) -> list[str]:
    """构造调用 auto_update 的 argv。未打包且有 .py 时走脚本，否则用 exe。"""
    extra = extra or []
    py = os.path.join(root, "auto_update.py")
    exe = os.path.join(root, "auto_update.exe")
    if (not is_frozen()) and os.path.isfile(py):
        return [sys.executable, py, *extra]
    if os.path.isfile(exe):
        return [exe, *extra]
    if os.path.isfile(py):
        return [sys.executable, py, *extra]
    raise FileNotFoundError("未找到 auto_update.exe 或 auto_update.py（目录: %s）" % root)


def resolve_python_script_argv(root: str, rel_py: str, extra: list[str] | None = None) -> list[str]:
    """调用仓库内 .py 脚本；frozen 且无 Python 时仅支持已打包的同名 exe。"""
    extra = extra or []
    base = os.path.splitext(os.path.basename(rel_py))[0]
    exe = os.path.join(root, base + ".exe")
    if os.path.isfile(exe):
        return [exe, *extra]
    py = os.path.join(root, rel_py.replace("/", os.sep))
    if os.path.isfile(py):
        return [sys.executable, py, *extra]
    raise FileNotFoundError("未找到 %s 或 %s" % (exe, py))
