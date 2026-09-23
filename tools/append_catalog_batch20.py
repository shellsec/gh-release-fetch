#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Batch20：第二批装机必备闭源软件 → open_page_only（lookup 打开官网）。"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS = os.path.join(ROOT, "apps")
BATCH: dict[tuple[str, str], list] = {}


def _add(plat: str, shard: str, apps: list):
    BATCH.setdefault((plat, shard), []).extend(apps)


def _page(aid, 简介, 分类, url, aliases):
    return {
        "id": aid,
        "简介": 简介,
        "分类": 分类,
        "aliases": list(aliases),
        "enabled": False,
        "open_page_only": True,
        "open_page_url": url,
        "url_hint": " ".join(aliases),
        "windows_installer": False,
        "process_name": "",
        "kill_before_install": False,
        "run_installer": False,
    }


def _on(plats, shard, aid, 简介, 分类, url, aliases, urls=None):
    urls = urls or {}
    for plat in plats:
        _add(plat, shard, [_page(aid, 简介, 分类, urls.get(plat, url), aliases)])


WDL = ("windows", "darwin", "linux")
WD = ("windows", "darwin")

# --- 办公 / 通讯 ---
_on(WDL, "04-办公.json", "microsoft_365",
    "Microsoft 365 / Office（官网分发，lookup 打开下载页；Linux 为网页版）", "办公",
    "https://www.microsoft.com/zh-cn/microsoft-365/download",
    ["office", "microsoft 365", "office 365", "微软办公", "Word", "Excel", "PPT"],
    urls={"linux": "https://www.office.com/"})
_on(WDL, "20-网络与通讯.json", "teams",
    "Microsoft Teams（官网分发，lookup 打开下载页）", "网络与通讯",
    "https://www.microsoft.com/zh-cn/microsoft-teams/download-app",
    ["teams", "Microsoft Teams", "微软会议"])
_on(WD, "20-网络与通讯.json", "wecom",
    "企业微信（官网分发，lookup 打开下载页）", "网络与通讯",
    "https://work.weixin.qq.com/#indexDownload",
    ["wecom", "企业微信", "wework", "wxwork"])
_on(("windows",), "20-网络与通讯.json", "foxmail",
    "Foxmail（腾讯邮箱客户端；官网分发，lookup 打开下载页）", "网络与通讯",
    "https://www.foxmail.com/",
    ["foxmail", "Foxmail", "腾讯邮箱"])

# --- 网盘 / 下载 ---
_on(WDL, "07-备份.json", "baidunetdisk",
    "百度网盘（官网分发，lookup 打开下载页）", "备份",
    "https://pan.baidu.com/download",
    ["baidunetdisk", "百度网盘", "百度云"])
_on(WD, "07-备份.json", "aliyundrive",
    "阿里云盘（官网分发，lookup 打开下载页）", "备份",
    "https://www.alipan.com/",
    ["aliyundrive", "alipan", "阿里云盘", "阿里网盘"])
_on(WD, "07-备份.json", "onedrive",
    "OneDrive（微软云盘；官网分发，lookup 打开下载页）", "备份",
    "https://www.microsoft.com/zh-cn/microsoft-365/onedrive/download",
    ["onedrive", "OneDrive", "微软云盘"])
_on(WDL, "07-备份.json", "dropbox",
    "Dropbox（官网分发，lookup 打开下载页）", "备份",
    "https://www.dropbox.com/downloading",
    ["dropbox", "Dropbox"])
_on(WD, "02-下载.json", "xunlei",
    "迅雷（官网分发，lookup 打开下载页）", "下载",
    "https://www.xunlei.com/",
    ["xunlei", "thunder", "迅雷"])

# --- 开发 IDE ---
_on(WDL, "12-开发.json", "intellij",
    "IntelliJ IDEA（JetBrains；lookup 打开官网，不自动下载）", "开发",
    "https://www.jetbrains.com/idea/download/",
    ["intellij", "idea", "IntelliJ", "IntelliJ IDEA"])
_on(WDL, "12-开发.json", "pycharm",
    "PyCharm（JetBrains Python IDE；lookup 打开官网）", "开发",
    "https://www.jetbrains.com/pycharm/download/",
    ["pycharm", "PyCharm"])
_on(WDL, "12-开发.json", "webstorm",
    "WebStorm（JetBrains 前端 IDE；lookup 打开官网）", "开发",
    "https://www.jetbrains.com/webstorm/download/",
    ["webstorm", "WebStorm"])
_on(("windows",), "12-开发.json", "visual_studio",
    "Visual Studio（微软 IDE，非 VS Code；lookup 打开下载页）", "开发",
    "https://visualstudio.microsoft.com/zh-hans/downloads/",
    ["visual studio", "vs2022", "Visual Studio", "微软IDE"])

# --- 文档 / 设计 ---
_on(WDL, "26-编辑器.json", "typora",
    "Typora（Markdown 编辑器；官网分发，lookup 打开下载页）", "编辑器",
    "https://typora.io/",
    ["typora", "Typora"])
_on(WDL, "04-办公.json", "xmind",
    "XMind（思维导图；官网分发，lookup 打开下载页）", "办公",
    "https://xmind.com/download/",
    ["xmind", "XMind", "思维导图"])
_on(WDL, "05-办公与设计.json", "figma",
    "Figma 桌面版（官网分发；Linux 打开网页版）", "办公与设计",
    "https://www.figma.com/downloads/",
    ["figma", "Figma"],
    urls={"linux": "https://www.figma.com/"})
_on(WDL, "04-办公.json", "adobe_reader",
    "Adobe Acrobat Reader（PDF 阅读；官网分发，lookup 打开下载页）", "办公",
    "https://get.adobe.com/cn/reader/",
    ["adobe reader", "acrobat", "Adobe Reader", "Adobe Acrobat", "PDF阅读器"])

# --- 娱乐 ---
_on(WDL, "22-音视频.json", "spotify",
    "Spotify（官方客户端；lookup 打开下载页。开源替代见 spotube）", "音视频",
    "https://www.spotify.com/download",
    ["spotify", "Spotify"],
    urls={
        "windows": "https://www.spotify.com/download/windows/",
        "darwin": "https://www.spotify.com/download/mac/",
        "linux": "https://www.spotify.com/download/linux/",
    })
_on(WD, "14-游戏.json", "epic_games",
    "Epic Games 启动器（官网分发，lookup 打开下载页）", "游戏",
    "https://store.epicgames.com/zh-CN/download",
    ["epic", "epic games", "Epic", "Epic Games"])
_on(WDL, "22-音视频.json", "netease_cloud_music",
    "网易云音乐（官网分发，lookup 打开下载页）", "音视频",
    "https://music.163.com/#/download",
    ["netease", "网易云", "网易云音乐", "cloudmusic"])
_on(WD, "22-音视频.json", "qqmusic",
    "QQ 音乐（官网分发，lookup 打开下载页）", "音视频",
    "https://y.qq.com/download/download.html",
    ["qqmusic", "QQ音乐", "qq 音乐"])
_on(WD, "22-音视频.json", "capcut",
    "剪映 / CapCut（字节剪辑；官网分发，lookup 打开下载页）", "音视频",
    "https://www.capcut.cn/",
    ["capcut", "jianying", "剪映", "剪映专业版"])


def _load_existing(plat: str) -> set[str]:
    ids: set[str] = set()
    d = os.path.join(APPS, plat)
    if not os.path.isdir(d):
        return ids
    for fn in os.listdir(d):
        if not fn.endswith(".json"):
            continue
        with open(os.path.join(d, fn), encoding="utf-8") as f:
            for item in json.load(f):
                if isinstance(item, dict) and item.get("id"):
                    ids.add(item["id"].strip())
    return ids


def _merge(dry: bool) -> tuple[int, int]:
    added = skipped = 0
    plat_ids: dict[str, set[str]] = {}
    for (plat, shard), apps in sorted(BATCH.items()):
        path = os.path.join(APPS, plat, shard)
        data = json.load(open(path, encoding="utf-8")) if os.path.isfile(path) else []
        if plat not in plat_ids:
            plat_ids[plat] = _load_existing(plat)
        seen = plat_ids[plat]
        file_ids = {(a.get("id") or "").strip() for a in data if isinstance(a, dict)}
        for app in apps:
            aid = (app.get("id") or "").strip()
            if aid in seen or aid in file_ids:
                skipped += 1
                continue
            data.append(app)
            seen.add(aid)
            file_ids.add(aid)
            added += 1
        if not dry:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
            print(f"Wrote {path} ({len(data)} entries)")
    return added, skipped


def main():
    dry = "--dry-run" in sys.argv
    a, s = _merge(dry)
    print(f"{'dry-run' if dry else 'done'}: +{a} skip {s}")


if __name__ == "__main__":
    main()
