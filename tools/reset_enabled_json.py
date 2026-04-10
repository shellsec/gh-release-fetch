#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
将所有应用配置 JSON 里的 enabled 一律写为 false（改磁盘文件）。

支持布局：
  - apps/windows/*.json（数组）
  - apps/darwin/*.json、apps/linux/*.json（数组分片）；若无分片则仍支持 apps/darwin.json、apps/linux.json
  - 根目录 apps.json（单文件，含 platforms.windows|darwin|linux）

用法：
  python tools/reset_enabled_json.py
  python tools/reset_enabled_json.py --dry-run
"""

import argparse
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _dump(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def reset_app_list(items):
    """返回本列表内被改写的条目数。"""
    n = 0
    if not isinstance(items, list):
        return n
    for app in items:
        if isinstance(app, dict):
            app["enabled"] = False
            n += 1
    return n


def process_apps_dir(apps_dir, dry_run):
    total = 0
    files = []
    win = os.path.join(apps_dir, "windows")
    if os.path.isdir(win):
        for name in sorted(os.listdir(win)):
            if not name.endswith(".json"):
                continue
            files.append(os.path.join(win, name))
    for plat in ("darwin", "linux"):
        sub = os.path.join(apps_dir, plat)
        used_dir = False
        if os.path.isdir(sub):
            names = [n for n in sorted(os.listdir(sub)) if n.endswith(".json")]
            if names:
                for name in names:
                    files.append(os.path.join(sub, name))
                used_dir = True
        if not used_dir:
            p = os.path.join(apps_dir, "%s.json" % plat)
            if os.path.isfile(p):
                files.append(p)

    for path in files:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "apps" in data:
            inner = data["apps"]
            if not isinstance(inner, list):
                print("跳过（非数组）:", path, file=sys.stderr)
                continue
            n = reset_app_list(inner)
            total += n
            print("%s %s 条%s" % (path, n, "（未写入）" if dry_run else ""))
            if not dry_run:
                _dump(path, data)
        elif isinstance(data, list):
            n = reset_app_list(data)
            total += n
            print("%s %s 条%s" % (path, n, "（未写入）" if dry_run else ""))
            if not dry_run:
                _dump(path, data)
        else:
            print("跳过（格式不符）:", path, file=sys.stderr)
    return total


def process_monolith(path, dry_run):
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    total = 0
    platforms = cfg.get("platforms")
    if isinstance(platforms, dict):
        for plat in ("windows", "darwin", "linux"):
            block = platforms.get(plat)
            if isinstance(block, list):
                total += reset_app_list(block)
    legacy = cfg.get("apps")
    if isinstance(legacy, list):
        total += reset_app_list(legacy)
    print("%s 合计 %s 条%s" % (path, total, "（未写入）" if dry_run else ""))
    if not dry_run and total:
        _dump(path, cfg)
    return total


def main():
    ap = argparse.ArgumentParser(description="将所有应用条目的 enabled 写回 false")
    ap.add_argument(
        "--root",
        default=SCRIPT_DIR,
        help="仓库根目录（默认：本脚本上级目录）",
    )
    ap.add_argument("--dry-run", action="store_true", help="只统计，不写文件")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    apps_dir = os.path.join(root, "apps")
    monolith = os.path.join(root, "apps.json")

    grand = 0
    if os.path.isfile(os.path.join(apps_dir, "root.json")):
        grand += process_apps_dir(apps_dir, args.dry_run)
    if os.path.isfile(monolith):
        grand += process_monolith(monolith, args.dry_run)

    if grand == 0 and not os.path.isfile(os.path.join(apps_dir, "root.json")) and not os.path.isfile(monolith):
        print("未找到 apps/ 或 apps.json", file=sys.stderr)
        sys.exit(1)

    print("共计处理条目数:", grand)
    if args.dry_run:
        print("（dry-run，未修改任何文件）")


if __name__ == "__main__":
    main()
