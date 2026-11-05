#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
按根目录 saved_apps_<platform>.json 批量开启 enabled 并执行 auto_update。

用法：
  python tools/run_saved_apps.py
  python tools/run_saved_apps.py windows
  python tools/run_saved_apps.py saved_apps_windows.json
  python tools/run_saved_apps.py --list my_apps_windows.json --skip-enable
  python tools/run_saved_apps.py --dry-run windows
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime

if getattr(sys, "frozen", False):
    SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if not getattr(sys, "frozen", False) and SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from tools.ghrf_runtime import resolve_auto_update_argv  # noqa: E402

from tools.app_list import (  # noqa: E402
    CATALOGS,
    PLATFORMS,
    default_list_basename,
    load_list,
    remove_item,
    resolve_list_path,
    save_hits_by_platform,
)
from tools.ui_lang import t  # noqa: E402


def detect_platform() -> str:
    if sys.platform == "win32":
        return "windows"
    if sys.platform == "darwin":
        return "darwin"
    return "linux"


def infer_platform(data: dict, fallback: str) -> str:
    plat = (data.get("platform") or "").strip().lower()
    if plat in PLATFORMS:
        return plat
    items = data.get("items") or []
    plats = {(r.get("platform") or "").lower() for r in items if r.get("platform")}
    plats.discard("")
    if len(plats) == 1:
        return next(iter(plats))
    return fallback


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="按 saved_apps_*.json 批量更新应用")
    ap.add_argument(
        "target",
        nargs="?",
        default="",
        help="平台名 windows|darwin|linux，或列表文件路径（默认当前系统 + saved_apps_<平台>.json）",
    )
    ap.add_argument("--list", dest="list_path", default="", help="显式指定列表 JSON 路径")
    ap.add_argument("--platform", default="", help="传给 auto_update 的平台")
    ap.add_argument("--skip-enable", action="store_true", help="不写入 enabled，仅按 id 更新")
    ap.add_argument("--dry-run", action="store_true", help="只预览，不修改 JSON、不下载")
    ap.add_argument("--insecure", action="store_true", help="传给 auto_update.py")
    ap.add_argument("--apps-dir", default="", help="传给 auto_update / apply 的配置目录")
    ap.add_argument("--manage", action="store_true", help="查看、移除或批量下载个人更新清单")
    args = ap.parse_args(argv)

    default_plat = args.platform or detect_platform()
    list_arg = args.list_path or args.target
    list_path = resolve_list_path(SCRIPT_DIR, list_arg or None, default_plat)
    if args.manage:
        paths = [list_path] if list_arg else [
            os.path.join(SCRIPT_DIR, default_list_basename(platform))
            for platform in PLATFORMS
        ]
        if not list_arg and os.environ.get("SAVED_APPS_LIST", "").strip() and list_path not in paths:
            paths.append(list_path)
        args.skip_enable = True
        return manage_lists(paths, args, default_plat)
    return run_list(list_path, args, default_plat)


def import_download_history(dry_run: bool) -> None:
    from lookup_app import print_hits, prompt_choose_hits, search_apps

    platforms_by_id = {}
    downloaded = set()
    start = re.compile(r" - INFO - === \[([^\]]+)\] 开始 === \[平台: ([^\]]+)\]")
    success = re.compile(r" - INFO - \[([^\]]+)\] 安装包已下载: ")
    try:
        with open(os.path.join(SCRIPT_DIR, "update_log.txt"), encoding="utf-8", errors="replace") as log:
            for line in log:
                match = start.search(line)
                if match:
                    app_id, platform = match.groups()
                    platforms_by_id.setdefault(app_id, set()).add(platform)
                match = success.search(line)
                if match:
                    app_id = match[1]
                    downloaded.add(app_id)
    except FileNotFoundError:
        print(t("saved.no_log"))
        return
    except OSError as error:
        print(error, file=sys.stderr)
        return

    keys = {
        (next(iter(platforms_by_id[app_id])), app_id)
        for app_id in downloaded
        if len(platforms_by_id.get(app_id, ())) == 1
    }
    matches = {}
    for directory in dict.fromkeys([*(row[1] for row in CATALOGS), "apps-custom"]):
        for hit in search_apps(os.path.join(SCRIPT_DIR, directory), "", min_score=0):
            key = (hit["platform"], hit["id"])
            if hit["downloadable"] and key in keys:
                matches.setdefault(key, []).append(hit)
    hits = [rows[0] for _, rows in sorted(matches.items()) if len(rows) == 1]
    print(t("saved.history_result", len(hits), len(downloaded) - len(hits)))
    if not hits:
        return
    print_hits(hits)
    chosen = prompt_choose_hits(hits)
    if not isinstance(chosen, list) or not chosen:
        return
    if dry_run:
        print(t("saved.import_dry"))
    else:
        try:
            save_hits_by_platform(SCRIPT_DIR, chosen, os.path.join(SCRIPT_DIR, "apps"))
        except (OSError, ValueError) as error:
            print(error, file=sys.stderr)


def manage_lists(paths: list[str], args: argparse.Namespace, default_plat: str) -> int:
    exit_code = 0
    try:
        while True:
            available = [path for path in paths if os.path.isfile(path)]
            if not available:
                print(t("saved.empty"))
            print("\n" + t("catalog.saved"))
            for number, path in enumerate(available, 1):
                print("  %d  %s" % (number, os.path.basename(path)))
            choice = input(t("saved.lists")).strip().lower()
            if choice in ("", "b", "q", "0"):
                return exit_code
            if choice == "i":
                import_download_history(args.dry_run)
                continue
            if choice == "a" and available:
                exit_code = download_batch(available, args, default_plat)
                continue
            if not choice.isdecimal() or not 1 <= int(choice) <= len(available):
                print(t("common.invalid_choice"))
                continue
            path = available[int(choice) - 1]
            while True:
                try:
                    items = load_list(path)["items"]
                except (OSError, ValueError) as error:
                    print(error, file=sys.stderr)
                    break
                print("\n" + os.path.basename(path))
                for number, item in enumerate(items, 1):
                    print("  %d  %s  %s" % (number, item.get("id", ""), item.get("简介", "")))
                if not items:
                    print(t("saved.no_items"))
                    break
                choice = input(t("saved.items")).strip().lower()
                if choice in ("", "b", "0"):
                    break
                if choice == "q":
                    return exit_code
                if choice == "a":
                    exit_code = download_batch([path], args, default_plat)
                    continue
                if not choice.isdecimal() or not 1 <= int(choice) <= len(items):
                    print(t("common.invalid_choice"))
                    continue
                item = items[int(choice) - 1]
                if input(t("saved.remove", item.get("id", ""))).strip().lower() != "y":
                    continue
                if args.dry_run:
                    print(t("saved.remove_dry"))
                    continue
                try:
                    if remove_item(path, item):
                        print(t("saved.removed"))
                except (OSError, ValueError) as error:
                    print(error, file=sys.stderr)
    except (EOFError, KeyboardInterrupt):
        return exit_code


def download_batch(paths: list[str], args: argparse.Namespace, default_plat: str) -> int:
    root = os.path.join(SCRIPT_DIR, "batch_downloads")
    if args.dry_run:
        folder = os.path.join(root, "preview")
    else:
        os.makedirs(root, exist_ok=True)
        prefix = datetime.now().strftime("%Y%m%d-%H%M%S-")
        folder = tempfile.mkdtemp(prefix=prefix, dir=root)
    results = [run_list(path, args, default_plat, batch_dir=folder) for path in paths]
    print(t("saved.result", sum(code == 0 for code in results), len(results)))
    if not args.dry_run:
        if any(files for _, _, files in os.walk(folder)):
            print(t("saved.folder", folder))
            opener = {"win32": "explorer", "darwin": "open"}.get(sys.platform, "xdg-open")
            try:
                subprocess.Popen([opener, folder])
            except OSError as error:
                print(error, file=sys.stderr)
        else:
            for directory, _, _ in os.walk(folder, topdown=False):
                try:
                    os.rmdir(directory)
                except OSError:
                    pass
    return int(any(results))


def run_list(list_path: str, args: argparse.Namespace, default_plat: str, batch_dir: str = "") -> int:

    if not os.path.isfile(list_path):
        hint = default_list_basename(default_plat)
        print("[ERROR] 未找到列表文件: %s" % list_path, file=sys.stderr)
        print("请先用 lookup_app 保存，或指定列表路径:", file=sys.stderr)
        print("  lookup_app.bat --platform %s --save 关键词" % default_plat, file=sys.stderr)
        print("  run_saved_apps.bat my_list.json", file=sys.stderr)
        print("  set SAVED_APPS_LIST=my_list.json  再 run_saved_apps.bat", file=sys.stderr)
        print("默认（未指定时）: %s（相对仓库根）" % hint, file=sys.stderr)
        return 1

    try:
        data = load_list(list_path)
    except (OSError, ValueError) as e:
        print("[ERROR] %s" % e, file=sys.stderr)
        return 1

    items = [r for r in (data.get("items") or []) if (r.get("id") or "").strip()]
    if not items:
        print("列表为空，无需处理。")
        return 0

    platform = infer_platform(data, default_plat)
    ids = sorted({(r.get("id") or "").strip() for r in items})
    groups: dict[tuple[str, str], set[str]] = {}
    for row in items:
        source = args.apps_dir
        if not source:
            # Saved paths include the catalog root, e.g. apps-tv/android_tv/08-....json.
            prefix = (row.get("path") or "").replace("\\", "/").split("/", 1)[0]
            if prefix and os.path.isfile(os.path.join(SCRIPT_DIR, prefix, "root.json")):
                source = prefix
        row_platform = args.platform or row.get("platform") or platform
        groups.setdefault((source, row_platform), set()).add(row["id"].strip())

    commands = []
    for (source, row_platform), group_ids in sorted(groups.items()):
        command_args = ["--platform", row_platform, *sorted(group_ids)]
        if source:
            command_args.extend(["--apps-dir", source])
        if args.insecure:
            command_args.append("--insecure")
        if batch_dir:
            command_args.extend(["--batch-download-dir", batch_dir])
        commands.append(resolve_auto_update_argv(SCRIPT_DIR, command_args))
    print("列表: %s（%d 条，平台 %s）" % (list_path, len(items), platform))
    print("应用 id:", ", ".join(ids))

    if args.dry_run:
        if not args.skip_enable:
            print("（dry-run：将 apply enabled）")
        for command in commands:
            print("[dry-run] 将执行: %s" % " ".join(command))
        return 0

    if not args.skip_enable:
        snap_arg = list_path
        try:
            if os.path.commonpath([SCRIPT_DIR, list_path]) == SCRIPT_DIR:
                snap_arg = os.path.relpath(list_path, SCRIPT_DIR)
        except ValueError:
            pass  # 不同盘符等：保留绝对路径
        print("\n[1/2] 开启 enabled …")
        if getattr(sys, "frozen", False):
            from tools import apply_enabled_snapshot as apply_mod

            old_argv = sys.argv
            sys.argv = [
                "apply_enabled_snapshot.py",
                "--root",
                SCRIPT_DIR,
                "--snapshot-path",
                snap_arg,
            ]
            try:
                apply_mod.main()
            except SystemExit as e:
                code = e.code
                if code not in (None, 0):
                    return int(code) if isinstance(code, int) else 1
            finally:
                sys.argv = old_argv
        else:
            apply_cmd = [
                sys.executable,
                os.path.join(SCRIPT_DIR, "tools", "apply_enabled_snapshot.py"),
                "--root",
                SCRIPT_DIR,
                "--snapshot-path",
                snap_arg,
            ]
            r = subprocess.run(apply_cmd, cwd=SCRIPT_DIR)
            if r.returncode != 0:
                return r.returncode

    print("\n[2/2] 执行更新 …")
    exit_code = 0
    for command in commands:
        result = subprocess.run(command, cwd=SCRIPT_DIR)
        if result.returncode:
            exit_code = result.returncode
    return exit_code


if __name__ == "__main__":
    from tools.ghrf_runtime import run_cli
    sys.exit(run_cli(main))
