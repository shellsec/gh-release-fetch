#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Batch21：macOS 装机必备（相对 Android 缺口）→ open_page_only。"""
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


def _on(plats, shard, aid, 简介, 分类, url, aliases):
    for plat in plats:
        _add(plat, shard, [_page(aid, 简介, 分类, url, aliases)])


D = ("darwin",)

# --- 通讯 / 社交 ---
C20, S20 = "网络与通讯", "20-网络与通讯.json"
_on(D, S20, "facebook", "Facebook（无官方 Mac 客户端；lookup 打开网页）", C20,
    "https://www.facebook.com/", ["facebook", "fb", "脸书"])
_on(D, S20, "instagram", "Instagram（无官方 Mac 客户端；lookup 打开网页）", C20,
    "https://www.instagram.com/", ["instagram", "ins", "ig", "Instagram"])
_on(D, S20, "messenger", "Messenger 桌面版（官网分发，lookup 打开下载页）", C20,
    "https://www.messenger.com/desktop", ["messenger", "facebook messenger", "FB Messenger"])
_on(D, S20, "whatsapp", "WhatsApp Desktop（官网分发，lookup 打开下载页）", C20,
    "https://www.whatsapp.com/download", ["whatsapp", "WhatsApp"])
_on(D, S20, "weibo", "微博（无官方 Mac 客户端；lookup 打开网页）", C20,
    "https://weibo.com/", ["weibo", "微博"])
_on(D, S20, "reddit", "Reddit（无官方 Mac 客户端；lookup 打开网页）", C20,
    "https://www.reddit.com/", ["reddit", "Reddit"])
_on(D, S20, "snapchat", "Snapchat（无官方 Mac 客户端；lookup 打开网页）", C20,
    "https://www.snapchat.com/", ["snapchat", "Snapchat"])
_on(D, S20, "skype", "Skype（官网分发，lookup 打开下载页）", C20,
    "https://www.skype.com/get-skype/", ["skype", "Skype"])
_on(D, S20, "line", "LINE Desktop（官网分发，lookup 打开下载页）", C20,
    "https://line.me/download", ["line", "LINE"])
_on(D, S20, "twitter", "X / Twitter（无官方 Mac 客户端；lookup 打开网页）", C20,
    "https://x.com/", ["twitter", "x.com", "推特", "X"])
_on(D, S20, "threads", "Threads（无官方 Mac 客户端；lookup 打开网页）", C20,
    "https://www.threads.net/", ["threads", "Threads"])

# --- 音视频 / 短视频 ---
C22, S22 = "音视频", "22-音视频.json"
_on(D, S22, "youtube", "YouTube（无官方 Mac 客户端；lookup 打开网页。下载器用 youtube_downloader_gui）", C22,
    "https://www.youtube.com/", ["youtube", "YouTube", "油管"])
_on(D, S22, "bilibili", "哔哩哔哩（官网分发，lookup 打开客户端下载页）", C22,
    "https://app.bilibili.com/", ["bilibili", "b站", "哔哩哔哩"])
_on(D, S22, "netflix", "Netflix（Mac App Store；lookup 打开商店页）", C22,
    "https://apps.apple.com/app/netflix/id363590051", ["netflix", "Netflix"])
_on(D, S22, "douyin", "抖音（无官方 Mac 客户端；lookup 打开网页）", C22,
    "https://www.douyin.com/", ["douyin", "抖音", "tiktok中国"])
_on(D, S22, "tiktok", "TikTok（无官方 Mac 客户端；lookup 打开网页）", C22,
    "https://www.tiktok.com/", ["tiktok", "TikTok"])
_on(D, S22, "kuaishou", "快手（无官方 Mac 客户端；lookup 打开网页）", C22,
    "https://www.kuaishou.com/", ["kuaishou", "快手"])
_on(D, S22, "youku", "优酷（无官方 Mac 客户端；lookup 打开网页）", C22,
    "https://www.youku.com/", ["youku", "优酷"])
_on(D, S22, "iqiyi", "爱奇艺（无官方 Mac 客户端；lookup 打开网页）", C22,
    "https://www.iqiyi.com/", ["iqiyi", "爱奇艺"])

# --- 社区 ---
C03, S03 = "写作", "03-写作.json"
_on(D, S03, "xiaohongshu", "小红书（无官方 Mac 客户端；lookup 打开网页）", C03,
    "https://www.xiaohongshu.com/", ["xiaohongshu", "小红书", "rednote", "xhs"])
_on(D, S03, "zhihu", "知乎（无官方 Mac 客户端；lookup 打开网页）", C03,
    "https://www.zhihu.com/", ["zhihu", "知乎"])

# --- 网盘 ---
_on(D, "07-备份.json", "googledrive",
    "Google Drive for desktop（官网分发，lookup 打开下载页）", "备份",
    "https://www.google.com/drive/download/",
    ["google drive", "googledrive", "谷歌云盘"])

# --- 办公 ---
_on(D, "04-办公.json", "google_docs",
    "Google 文档（网页版；lookup 打开）", "办公",
    "https://docs.google.com/",
    ["google docs", "谷歌文档"])
_on(D, "04-办公.json", "canva",
    "Canva（官网分发，lookup 打开下载页）", "办公",
    "https://www.canva.com/download/",
    ["canva", "Canva"])

# --- 浏览器 ---
_on(D, "18-网络.json", "opera",
    "Opera（官网分发，lookup 打开下载页）", "网络",
    "https://www.opera.com/download",
    ["opera", "Opera"])

# --- 远程 / 会议 ---
_on(D, "21-远程与协作.json", "meet",
    "Google Meet（网页版；lookup 打开）", "远程与协作",
    "https://meet.google.com/",
    ["google meet", "meet", "谷歌会议"])

# --- AI ---
_on(D, "01-AI.json", "chatgpt",
    "ChatGPT 官方 Mac 客户端（lookup 打开下载页）", "AI",
    "https://chatgpt.com/download/",
    ["chatgpt", "ChatGPT", "openai"])
_on(D, "01-AI.json", "gemini",
    "Google Gemini（网页版；lookup 打开）", "AI",
    "https://gemini.google.com/",
    ["gemini", "Gemini", "bard"])
_on(D, "01-AI.json", "copilot",
    "Microsoft Copilot（Mac App Store；lookup 打开商店页）", "AI",
    "https://apps.apple.com/app/microsoft-copilot/id6472538445",
    ["copilot", "Copilot"])

# --- 金融 ---
_on(D, "27-金融与股票.json", "alipay",
    "支付宝（无官方 Mac 客户端；lookup 打开官网）", "金融与股票",
    "https://mobile.alipay.com/",
    ["alipay", "支付宝"])
_on(D, "27-金融与股票.json", "paypal",
    "PayPal（网页版；lookup 打开）", "金融与股票",
    "https://www.paypal.com/",
    ["paypal", "PayPal"])

# --- 游戏 ---
_on(D, "14-游戏.json", "taptap",
    "TapTap（官网；lookup 打开）", "游戏",
    "https://www.taptap.cn/",
    ["taptap", "TapTap"])

# --- 工具：地图 / 邮箱 / 购物 / 出行 ---
C11, S11 = "工具", "11-工具.json"
_on(D, S11, "google_maps", "Google 地图（网页版；lookup 打开。开源客户端见 organicmaps）", C11,
    "https://maps.google.com/", ["google maps", "谷歌地图", "maps"])
_on(D, S11, "amap", "高德地图（无官方 Mac 客户端；lookup 打开官网）", C11,
    "https://mobile.amap.com/", ["amap", "高德", "高德地图"])
_on(D, S11, "baidu_map", "百度地图（无官方 Mac 客户端；lookup 打开网页）", C11,
    "https://map.baidu.com/", ["baidu map", "百度地图"])
_on(D, S11, "gmail", "Gmail（网页版；lookup 打开）", C11,
    "https://mail.google.com/", ["gmail", "Gmail"])
_on(D, S11, "google_keep", "Google Keep（网页版；lookup 打开）", C11,
    "https://keep.google.com/", ["keep", "google keep"])
_on(D, S11, "google_photos", "Google 相册（网页版；lookup 打开）", C11,
    "https://photos.google.com/", ["google photos", "谷歌相册"])
_on(D, S11, "taobao", "淘宝（无官方 Mac 客户端；lookup 打开网页）", C11,
    "https://www.taobao.com/", ["taobao", "淘宝"])
_on(D, S11, "jd", "京东（无官方 Mac 客户端；lookup 打开网页）", C11,
    "https://www.jd.com/", ["jd", "京东", "jingdong"])
_on(D, S11, "pinduoduo", "拼多多（无官方 Mac 客户端；lookup 打开网页）", C11,
    "https://www.pinduoduo.com/", ["pinduoduo", "拼多多", "pdd"])
_on(D, S11, "meituan", "美团（无官方 Mac 客户端；lookup 打开网页）", C11,
    "https://www.meituan.com/", ["meituan", "美团"])
_on(D, S11, "didi", "滴滴出行（无官方 Mac 客户端；lookup 打开网页）", C11,
    "https://www.didiglobal.com/", ["didi", "滴滴"])
_on(D, S11, "amazon", "Amazon（网页版；lookup 打开）", C11,
    "https://www.amazon.com/", ["amazon", "亚马逊"])


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
            os.makedirs(os.path.dirname(path), exist_ok=True)
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
