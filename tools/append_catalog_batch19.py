#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Batch19：装机必备闭源/官网分发软件 → open_page_only（lookup 可搜、直接打开官网）。"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS = os.path.join(ROOT, "apps")
BATCH: dict[tuple[str, str], list] = {}
UPSERT: dict[tuple[str, str], list] = {}


def _add(plat: str, shard: str, apps: list):
    BATCH.setdefault((plat, shard), []).extend(apps)


def _upsert(plat: str, shard: str, apps: list):
    UPSERT.setdefault((plat, shard), []).extend(apps)


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
        app = _page(aid, 简介, 分类, urls.get(plat, url), aliases)
        _add(plat, shard, [app])


WDL = ("windows", "darwin", "linux")
WD = ("windows", "darwin")

# --- 远程 ---
_on(WDL, "21-远程与协作.json", "todesk",
    "ToDesk（远程桌面；闭源官网分发，lookup 打开下载页，不自动下载）", "远程与协作",
    "https://www.todesk.com/download.html",
    ["todesk", "ToDesk", "向日葵同类", "远程桌面"])
_on(WDL, "21-远程与协作.json", "anydesk",
    "AnyDesk（远程桌面；闭源官网分发，lookup 打开下载页）", "远程与协作",
    "https://anydesk.com/zhs/downloads",
    ["anydesk", "AnyDesk"])
_on(WDL, "21-远程与协作.json", "teamviewer",
    "TeamViewer（远程协助；闭源官网分发，lookup 打开下载页）", "远程与协作",
    "https://www.teamviewer.com/zh-cn/download/",
    ["teamviewer", "TeamViewer"])
_on(WDL, "21-远程与协作.json", "zoom",
    "Zoom（视频会议；闭源官网分发，lookup 打开下载页）", "远程与协作",
    "https://zoom.us/download",
    ["zoom", "Zoom", "视频会议"])

# --- 通讯 ---
_on(WDL, "20-网络与通讯.json", "wechat",
    "微信 PC 版（腾讯官网分发，lookup 打开下载页，不自动下载）", "网络与通讯",
    "https://pc.weixin.qq.com/",
    ["wechat", "weixin", "微信", "WeChat"],
    urls={
        "windows": "https://pc.weixin.qq.com/",
        "darwin": "https://mac.weixin.qq.com/",
        "linux": "https://linux.weixin.qq.com/",
    })
_on(WDL, "20-网络与通讯.json", "qq",
    "QQ（腾讯官网分发，lookup 打开下载页）", "网络与通讯",
    "https://im.qq.com/pcqq/",
    ["qq", "QQ", "腾讯QQ"],
    urls={
        "windows": "https://im.qq.com/pcqq/",
        "darwin": "https://im.qq.com/macqq/",
        "linux": "https://im.qq.com/linuxqq/",
    })
_on(WDL, "20-网络与通讯.json", "dingtalk",
    "钉钉（阿里办公通讯；官网分发，lookup 打开下载页）", "网络与通讯",
    "https://www.dingtalk.com/download",
    ["dingtalk", "钉钉", "dingding"])
_on(WDL, "20-网络与通讯.json", "feishu",
    "飞书 / Lark（字节协作套件；官网分发，lookup 打开下载页）", "网络与通讯",
    "https://www.feishu.cn/download",
    ["feishu", "lark", "飞书", "Lark"])
_on(WDL, "20-网络与通讯.json", "slack",
    "Slack（团队聊天；官网分发，lookup 打开下载页）", "网络与通讯",
    "https://slack.com/downloads",
    ["slack", "Slack"])
_on(WDL, "20-网络与通讯.json", "discord",
    "Discord（语音/社区；官网分发，lookup 打开下载页）", "网络与通讯",
    "https://discord.com/download",
    ["discord", "Discord"])

# --- 浏览器 ---
_on(WDL, "18-网络.json", "chrome",
    "Google Chrome（官网分发，lookup 打开下载页）", "网络",
    "https://www.google.com/chrome/",
    ["chrome", "google chrome", "谷歌浏览器", "Chrome"])
_on(WDL, "18-网络.json", "edge",
    "Microsoft Edge（官网分发，lookup 打开下载页）", "网络",
    "https://www.microsoft.com/edge/download",
    ["edge", "microsoft edge", "Edge", "微软浏览器"])
_on(WDL, "18-网络.json", "firefox",
    "Mozilla Firefox（官网安装包，lookup 打开下载页）", "网络",
    "https://www.mozilla.org/zh-CN/firefox/new/",
    ["firefox", "Firefox", "火狐"])

# --- 办公 / 笔记 / 游戏 ---
_on(WDL, "04-办公.json", "wps",
    "WPS 办公套件（金山官网分发，lookup 打开下载页）", "办公",
    "https://www.wps.cn/",
    ["wps", "WPS", "金山办公", "wps office"])
_on(WDL, "15-笔记.json", "notion",
    "Notion 桌面版（官网分发，lookup 打开下载页）", "笔记",
    "https://www.notion.com/desktop",
    ["notion", "Notion"])
_on(WDL, "14-游戏.json", "steam",
    "Steam（Valve 游戏平台；官网分发，lookup 打开下载页）", "游戏",
    "https://store.steampowered.com/about/",
    ["steam", "Steam"])

# --- 输入法 / 压缩 / 效率 ---
_on(WD, "16-系统.json", "sogou_pinyin",
    "搜狗输入法（官网分发，lookup 打开下载页）", "系统",
    "https://pinyin.sogou.com/",
    ["sogou", "搜狗", "搜狗输入法", "sogou pinyin"],
    urls={
        "windows": "https://pinyin.sogou.com/",
        "darwin": "https://pinyin.sogou.com/mac/",
    })
_on(WD, "11-工具.json", "bandizip",
    "Bandizip（压缩解压；官网分发，lookup 打开下载页）", "工具",
    "https://www.bandisoft.com/bandizip/",
    ["bandizip", "Bandizip"])
_on(("windows",), "11-工具.json", "winrar",
    "WinRAR（压缩解压；官网分发，lookup 打开下载页）", "工具",
    "https://www.winrar.com.cn/",
    ["winrar", "WinRAR", "rar"])
_on(WDL, "13-效率.json", "utools",
    "uTools（效率启动器；官网分发，lookup 打开下载页）", "效率",
    "https://www.u.tools/",
    ["utools", "uTools", "u工具"])
_on(("windows",), "13-效率.json", "listary",
    "Listary（文件搜索启动器；官网分发，lookup 打开下载页）", "效率",
    "https://www.listary.com/download",
    ["listary", "Listary"])
_on(("windows",), "22-音视频.json", "potplayer",
    "PotPlayer（本地播放器；官网分发，lookup 打开下载页）", "音视频",
    "https://potplayer.daum.net/",
    ["potplayer", "PotPlayer"])

# 已有占位：改成真正能打开官网
for plat in WDL:
    _upsert(plat, "12-开发.json", [{
        "id": "goland",
        "简介": "JetBrains GoLand IDE（商业/试用；lookup 打开官网，不自动下载。Go 语言运行时请搜 id=go）",
        "分类": "开发",
        "aliases": ["goland", "GoLand", "jetbrains go"],
        "enabled": False,
        "open_page_only": True,
        "open_page_url": "https://www.jetbrains.com/go/download/",
        "url_hint": "goland jetbrains",
        "windows_installer": False,
        "process_name": "",
        "kill_before_install": False,
        "run_installer": False,
    }])


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


def _merge(dry: bool) -> tuple[int, int, int]:
    added = skipped = updated = 0
    plat_ids: dict[str, set[str]] = {}

    for (plat, shard), apps in sorted(UPSERT.items()):
        path = os.path.join(APPS, plat, shard)
        data = json.load(open(path, encoding="utf-8")) if os.path.isfile(path) else []
        by_id = {(a.get("id") or "").strip(): i for i, a in enumerate(data) if isinstance(a, dict)}
        for app in apps:
            aid = (app.get("id") or "").strip()
            if aid in by_id:
                data[by_id[aid]] = app
                updated += 1
            else:
                data.append(app)
                added += 1
        if not dry:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
            print(f"Upsert {path} ({len(data)} entries)")

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
    return added, skipped, updated


def main():
    dry = "--dry-run" in sys.argv
    a, s, u = _merge(dry)
    print(f"{'dry-run' if dry else 'done'}: +{a} skip {s} upsert {u}")


if __name__ == "__main__":
    main()
