#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""apps-mobile batch7：Facebook / Instagram / Telegram 等社交通讯（GitHub APK 或打开官网/商店）。"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOBILE = os.path.join(ROOT, "apps-mobile")
BATCH: dict[str, list] = {}


def _add(shard: str, apps: list):
    BATCH.setdefault(shard, []).extend(apps)


def _apk(**kw):
    d = {
        "enabled": False,
        "prefer_api_assets": True,
        "version_tag_as_on_github": True,
        "run_installer": False,
        "kill_before_install": False,
        "windows_installer": False,
        "process_name": "",
        "installer_extensions": [".apk"],
        "use_download_filename": True,
        "href_exclude_substrings": [
            "debug", ".aab", "test", "unsigned", "sources", ".json", ".txt",
        ],
    }
    d.update(kw)
    return d


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
        "run_installer": False,
        "kill_before_install": False,
        "windows_installer": False,
        "process_name": "",
    }


SH = "20-网络与通讯.json"
CAT = "网络与通讯"

# --- 官方无 GitHub APK：打开商店/官网 ---
_add(SH, [_page(
    "facebook",
    "Facebook 官方 Android（无 GitHub APK；lookup 打开 Play 商店页）",
    CAT,
    "https://play.google.com/store/apps/details?id=com.facebook.katana",
    ["facebook", "fb", "脸书"],
)])
_add(SH, [_page(
    "instagram",
    "Instagram 官方 Android（无 GitHub APK；lookup 打开 Play 商店页）",
    CAT,
    "https://play.google.com/store/apps/details?id=com.instagram.android",
    ["instagram", "ins", "ig", "Instagram"],
)])
_add(SH, [_page(
    "messenger",
    "Messenger 官方 Android（无 GitHub APK；lookup 打开 Play 商店页）",
    CAT,
    "https://play.google.com/store/apps/details?id=com.facebook.orca",
    ["messenger", "facebook messenger", "FB Messenger"],
)])
_add(SH, [_page(
    "whatsapp",
    "WhatsApp 官方 Android（无 GitHub APK；lookup 打开官网下载页）",
    CAT,
    "https://www.whatsapp.com/android",
    ["whatsapp", "WhatsApp", "wa"],
)])
_add(SH, [_page(
    "discord_android",
    "Discord 官方 Android（无 GitHub APK；lookup 打开 Play 商店页）",
    CAT,
    "https://play.google.com/store/apps/details?id=com.discord",
    ["discord", "Discord"],
)])
_add(SH, [_page(
    "twitter",
    "X / Twitter 官方 Android（无 GitHub APK；lookup 打开 Play 商店页）",
    CAT,
    "https://play.google.com/store/apps/details?id=com.twitter.android",
    ["twitter", "x.com", "推特", "X"],
)])
_add(SH, [_page(
    "telegram",
    "Telegram 官方 Android（Release 常无 Assets；lookup 打开官网 APK 页）",
    CAT,
    "https://telegram.org/android",
    ["telegram", "tg", "电报"],
)])
_add(SH, [_page(
    "threads",
    "Threads 官方 Android（无 GitHub APK；lookup 打开 Play 商店页）",
    CAT,
    "https://play.google.com/store/apps/details?id=com.instagram.barcelona",
    ["threads", "Threads"],
)])
_add(SH, [_page(
    "line",
    "LINE 官方 Android（无 GitHub APK；lookup 打开官网下载页）",
    CAT,
    "https://line.me/en/download",
    ["line", "LINE"],
)])

# --- 有 GitHub APK ---
_add(SH, [_apk(
    id="telegram_x",
    简介="Telegram X（开源 Android 客户端；GitHub APK）",
    分类=CAT,
    aliases=["telegram x", "telegramx", "Telegram X", "telegram"],
    installer_markers_match_all=True,
    installer_markers=["Telegram-X-", ".apk"],
    href_exclude_substrings=[
        "legacy", "lollipop", "debug", ".aab", "test", "unsigned", "sources",
    ],
    save_name="telegram_x.apk",
    releases_url="https://bgithub.xyz/TGX-Android/Telegram-X/releases",
    repo_path="TGX-Android/Telegram-X",
)])
_add(SH, [_apk(
    id="telegram_foss",
    简介="Telegram-FOSS（去闭源依赖的 Telegram Android；GitHub APK）",
    分类=CAT,
    aliases=["telegram foss", "Telegram-FOSS", "telegram"],
    installer_markers=[".apk"],
    href_exclude_substrings=["debug", ".aab", "unsigned", "sources"],
    save_name="telegram_foss.apk",
    releases_url="https://bgithub.xyz/Telegram-FOSS-Team/Telegram-FOSS/releases",
    repo_path="Telegram-FOSS-Team/Telegram-FOSS",
)])
_add(SH, [_apk(
    id="twidere",
    简介="Twidere（Twitter/X 开源客户端；GitHub F-Droid APK）",
    分类=CAT,
    aliases=["twidere", "twitter", "推特"],
    installer_markers_match_all=True,
    installer_markers=["twidere-fdroid-release", ".apk"],
    save_name="twidere.apk",
    releases_url="https://bgithub.xyz/TwidereProject/Twidere-Android/releases",
    repo_path="TwidereProject/Twidere-Android",
)])
_add(SH, [_apk(
    id="session_android",
    简介="Session（去中心化私密通讯 Android；universal play APK）",
    分类=CAT,
    aliases=["session", "Session"],
    installer_markers_match_all=True,
    installer_markers=["session-", "universal-play-release.apk"],
    href_exclude_substrings=["huawei", "arm64-v8a", "armeabi", "x86", ".aab", "debug"],
    save_name="session_android.apk",
    releases_url="https://bgithub.xyz/session-foundation/session-android/releases",
    repo_path="session-foundation/session-android",
)])


def main():
    dry = "--dry-run" in sys.argv
    total = 0
    for shard, apps in sorted(BATCH.items()):
        path = os.path.join(MOBILE, "android", shard)
        existing = json.load(open(path, encoding="utf-8")) if os.path.isfile(path) else []
        seen = {(a.get("id") or "").strip() for a in existing if isinstance(a, dict)}
        for app in apps:
            aid = (app.get("id") or "").strip()
            if aid in seen:
                continue
            existing.append(app)
            seen.add(aid)
            total += 1
        if not dry:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)
                f.write("\n")
            print("Wrote", path, "count", len(existing))
    print(f"{'dry-run' if dry else 'done'}: added {total}")


if __name__ == "__main__":
    main()
