#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Batch17：对照 ghxi.com/category/all 开源向条目，补未收录且有 GitHub Release 的项。"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS = os.path.join(ROOT, "apps")
BATCH: dict[tuple[str, str], list] = {}


def _add(plat: str, shard: str, apps: list):
    BATCH.setdefault((plat, shard), []).extend(apps)


def _b(**kw):
    d = {
        "enabled": False,
        "prefer_api_assets": True,
        "version_tag_as_on_github": True,
        "windows_installer": False,
        "process_name": "",
        "kill_before_install": False,
        "run_installer": False,
        "use_download_filename": True,
        "href_exclude_substrings": [
            "source", "src.", "-src", "symbols", "debug", "pdb",
            "sha256", ".sig", ".crt", ".asc", ".json", ".txt", ".md",
            "checksum", ".yml", ".blockmap", ".zsync", ".apk",
        ],
    }
    d.update(kw)
    return d


def _repo(repo: str) -> dict:
    return {
        "releases_url": f"https://bgithub.xyz/{repo}/releases",
        "repo_path": repo,
    }


def _e(plat, shard, aid, 简介, 分类, repo, **cfg):
    _add(plat, shard, [{"id": aid, "简介": 简介, "分类": 分类, **_b(**cfg), **_repo(repo)}])


# --- 下载 ---
_e("windows", "02-下载.json", "motrix_next",
   "MotrixNext（Motrix Tauri 重写版下载器；Windows x64 Setup）", "下载",
   "AnInsomniacy/motrix-next",
   installer_markers_match_all=True,
   installer_markers=["MotrixNext_", "x64-setup.exe"],
   href_exclude_substrings=["arm64", ".dmg", ".deb", "AppImage", ".rpm", ".sig"],
   installer_extensions=[".exe"], windows_installer=True, run_installer=True)
_e("darwin", "02-下载.json", "motrix_next",
   "MotrixNext（macOS Apple Silicon / 或 x64 dmg，优先 arm64）", "下载",
   "AnInsomniacy/motrix-next",
   installer_markers_match_all=True,
   installer_markers=["MotrixNext_", "aarch64.dmg"],
   href_exclude_substrings=[".exe", ".deb", "AppImage", "app.tar.gz", ".sig"],
   installer_extensions=[".dmg"])
_e("linux", "02-下载.json", "motrix_next",
   "MotrixNext（Linux amd64 AppImage）", "下载",
   "AnInsomniacy/motrix-next",
   installer_markers_match_all=True,
   installer_markers=["MotrixNext_", "amd64.AppImage"],
   href_exclude_substrings=[".exe", ".dmg", ".deb", ".rpm", "aarch64", ".sig"],
   installer_extensions=[".AppImage"])

_e("windows", "02-下载.json", "ghost_downloader",
   "Ghost Downloader（Python 多线程下载器；Windows x64 Setup）", "下载",
   "XiaoYouChR/Ghost-Downloader-3",
   installer_markers_match_all=True,
   installer_markers=["Ghost-Downloader-", "Windows-x86_64-Setup.exe"],
   href_exclude_substrings=["arm64", ".zip", ".apk", ".dmg", "AppImage", ".sig"],
   installer_extensions=[".exe"], windows_installer=True, run_installer=True)
_e("darwin", "02-下载.json", "ghost_downloader",
   "Ghost Downloader（macOS Apple Silicon dmg）", "下载",
   "XiaoYouChR/Ghost-Downloader-3",
   installer_markers_match_all=True,
   installer_markers=["Ghost-Downloader-", "macOS-arm64.dmg"],
   href_exclude_substrings=["x86_64", ".zip", ".apk", ".exe", ".sig"],
   installer_extensions=[".dmg"])
_e("linux", "02-下载.json", "ghost_downloader",
   "Ghost Downloader（Linux x86_64 AppImage）", "下载",
   "XiaoYouChR/Ghost-Downloader-3",
   installer_markers_match_all=True,
   installer_markers=["Ghost-Downloader-", "Linux-x86_64.AppImage"],
   href_exclude_substrings=["arm64", ".deb", ".exe", ".dmg", ".apk", ".sig"],
   installer_extensions=[".AppImage"])

_e("windows", "02-下载.json", "fluxdown",
   "FluxDown（Rust 多协议下载器；Windows x64 Setup）", "下载",
   "zerx-lab/FluxDown",
   installer_markers_match_all=True,
   installer_markers=["FluxDown-", "windows-x64-setup.exe"],
   href_exclude_substrings=["arm64", "portable", ".zip", ".dmg", "linux", ".sig"],
   installer_extensions=[".exe"], windows_installer=True, run_installer=True)
_e("darwin", "02-下载.json", "fluxdown",
   "FluxDown（macOS Apple Silicon dmg）", "下载",
   "zerx-lab/FluxDown",
   installer_markers_match_all=True,
   installer_markers=["FluxDown-", "macos-arm64.dmg"],
   href_exclude_substrings=["x64", ".tar.gz", "windows", "linux", ".sig"],
   installer_extensions=[".dmg"])
_e("linux", "02-下载.json", "fluxdown",
   "FluxDown（Linux x64 AppImage）", "下载",
   "zerx-lab/FluxDown",
   installer_markers_match_all=True,
   installer_markers=["FluxDown-", "linux-x64.AppImage"],
   href_exclude_substrings=[".deb", ".tar.gz", "windows", "macos", ".sig"],
   installer_extensions=[".AppImage"])

_e("windows", "02-下载.json", "xiadown",
   "XiaDown（资源库/视频下载管理；Windows x64 安装包）", "下载",
   "arnoldhao/xiadown",
   installer_markers_match_all=True,
   installer_markers=["xiadown-windows-x64-", "installer.exe"],
   href_exclude_substrings=[".zip", "macos", ".sha256", ".sig"],
   installer_extensions=[".exe"], windows_installer=True, run_installer=True)
_e("darwin", "02-下载.json", "xiadown",
   "XiaDown（macOS Apple Silicon dmg）", "下载",
   "arnoldhao/xiadown",
   installer_markers_match_all=True,
   installer_markers=["xiadown-macos-arm64-", ".dmg"],
   href_exclude_substrings=[".zip", "x64", "windows", ".sha256", ".sig"],
   installer_extensions=[".dmg"])

# --- 远程 ---
_e("windows", "21-远程与协作.json", "android_dex",
   "Android DEX（把安卓当桌面；基于 scrcpy，Windows zip）", "远程与协作",
   "Shrey113/Android-Dex",
   installer_markers_match_all=True,
   installer_markers=["Android_Dex_Windows", ".zip"],
   href_exclude_substrings=["macOS", "Linux", "pre_build", ".apk"],
   installer_extensions=[".zip"])
_e("darwin", "21-远程与协作.json", "android_dex",
   "Android DEX（macOS zip）", "远程与协作",
   "Shrey113/Android-Dex",
   installer_markers_match_all=True,
   installer_markers=["Android_Dex_macOS", ".zip"],
   href_exclude_substrings=["Windows", "Linux", "pre_build", ".apk"],
   installer_extensions=[".zip"])
_e("linux", "21-远程与协作.json", "android_dex",
   "Android DEX（Linux zip）", "远程与协作",
   "Shrey113/Android-Dex",
   installer_markers_match_all=True,
   installer_markers=["Android_Dex_Linux", ".zip"],
   href_exclude_substrings=["Windows", "macOS", "pre_build", ".apk"],
   installer_extensions=[".zip"])

_e("windows", "21-远程与协作.json", "qtscrcpy",
   "QtScrcpy（安卓投屏控制；Windows x64 zip）", "远程与协作",
   "barry-ran/QtScrcpy",
   installer_markers_match_all=True,
   installer_markers=["QtScrcpy-win-x64-", ".zip"],
   href_exclude_substrings=["x86", "mac", "ubuntu", "AppImage"],
   installer_extensions=[".zip"])
_e("darwin", "21-远程与协作.json", "qtscrcpy",
   "QtScrcpy（macOS Apple Silicon dmg）", "远程与协作",
   "barry-ran/QtScrcpy",
   installer_markers_match_all=True,
   installer_markers=["QtScrcpy-mac-arm64-", ".dmg"],
   href_exclude_substrings=["x64", "win", "ubuntu", "AppImage"],
   installer_extensions=[".dmg"])
_e("linux", "21-远程与协作.json", "qtscrcpy",
   "QtScrcpy（Linux x64 AppImage）", "远程与协作",
   "barry-ran/QtScrcpy",
   installer_markers_match_all=True,
   installer_markers=["QtScrcpy-ubuntu-x64-", ".AppImage"],
   href_exclude_substrings=["win", "mac", ".zip"],
   installer_extensions=[".AppImage"])

# --- 系统 / 工具 ---
_e("windows", "16-系统.json", "server_box",
   "Server Box（Linux 服务器状态与工具箱；Windows amd64 zip）", "系统",
   "lollipopkit/flutter_server_box",
   installer_markers_match_all=True,
   installer_markers=["ServerBox_v", "windows_amd64.zip"],
   href_exclude_substrings=[".apk", "AppImage", ".dmg", "legacy"],
   installer_extensions=[".zip"])
_e("darwin", "16-系统.json", "server_box",
   "Server Box（macOS dmg）", "系统",
   "lollipopkit/flutter_server_box",
   installer_markers_match_all=True,
   installer_markers=["ServerBox-", ".dmg"],
   href_exclude_substrings=[".apk", "AppImage", "windows", ".zip"],
   installer_extensions=[".dmg"])
_e("linux", "16-系统.json", "server_box",
   "Server Box（Linux amd64 AppImage）", "系统",
   "lollipopkit/flutter_server_box",
   installer_markers_match_all=True,
   installer_markers=["ServerBox_v", "amd64.AppImage"],
   href_exclude_substrings=["legacy", ".apk", "windows", ".dmg", "arm"],
   installer_extensions=[".AppImage"])

_e("windows", "16-系统.json", "windirstat",
   "WinDirStat（磁盘使用统计与清理；Windows x64 MSI）", "系统",
   "windirstat/windirstat",
   installer_markers_match_all=True,
   installer_markers=["WinDirStat-x64", ".msi"],
   href_exclude_substrings=["arm64", "x86", "Debug", "Hashes", ".7z", ".zip", ".msix"],
   installer_extensions=[".msi"], windows_installer=True, run_installer=True)

_e("windows", "11-工具.json", "leafview",
   "LeafView（极简图片查看器；Windows x64 安装包）", "工具",
   "sprout2000/leafview",
   installer_markers_match_all=True,
   installer_markers=["LeafView-", "win32-x64-installer.exe"],
   href_exclude_substrings=[".zip", "blockmap", ".yml", "darwin", "linux"],
   installer_extensions=[".exe"], windows_installer=True, run_installer=True)
_e("darwin", "11-工具.json", "leafview",
   "LeafView（macOS Apple Silicon dmg）", "工具",
   "sprout2000/leafview",
   installer_markers_match_all=True,
   installer_markers=["LeafView-", "darwin-arm64.dmg"],
   href_exclude_substrings=[".zip", "blockmap", ".yml", "darwin-x64", "win32", "linux"],
   installer_extensions=[".dmg"])
_e("linux", "11-工具.json", "leafview",
   "LeafView（Linux x86_64 AppImage）", "工具",
   "sprout2000/leafview",
   installer_markers_match_all=True,
   installer_markers=["LeafView-", "linux-x86_64.AppImage"],
   href_exclude_substrings=[".yml", "blockmap", "darwin", "win", ".deb", ".zip"],
   installer_extensions=[".AppImage"])

# --- 效率 / 游戏 / 音视频 / 多媒体 ---
_e("windows", "13-效率.json", "paper_todo",
   "PaperTodo（极简桌面便签/待办；Windows x64 自包含安装包）", "效率",
   "snownico0722/PaperTodo",
   installer_markers_match_all=True,
   installer_markers=["PaperTodo-", "self-contained.exe"],
   href_exclude_substrings=["no-runtime", ".sig", ".crt"],
   installer_extensions=[".exe"], windows_installer=True, run_installer=True)

_e("windows", "14-游戏.json", "open_speedy",
   "OpenSpeedy（开源游戏加速工具；Windows x64 MSI）", "游戏",
   "game1024/OpenSpeedy",
   installer_markers_match_all=True,
   installer_markers=["OpenSpeedy_", "x64_zh-CN.msi"],
   href_exclude_substrings=["portable", ".zip", ".sig"],
   installer_extensions=[".msi"], windows_installer=True, run_installer=True)

_e("windows", "14-游戏.json", "vita3k",
   "Vita3K（PS Vita 模拟器；Windows 请看 continuous Release zip）", "游戏",
   "Vita3K/Vita3K",
   version_tag_as_on_github=False,
   installer_markers_match_all=True,
   installer_markers=["windows-latest", ".zip"],
   href_exclude_substrings=["android", "macos", "ubuntu", "AppImage", ".apk", ".zsync"],
   installer_extensions=[".zip"])
# Vita3K may use different windows asset name - check: continuous has ubuntu/macos but maybe windows-latest.zip?
# From earlier assets: android, macos, ubuntu, AppImage - NO windows zip in list!
# Skip vita3k windows if no asset - remove and only add if exists

_e("windows", "22-音视频.json", "nipaplay",
   "NipaPlay Reload（跨平台本地视频/弹幕播放器；Windows x64 Setup）", "音视频",
   "AimesSoft/NipaPlay-Reload",
   installer_markers_match_all=True,
   installer_markers=["NipaPlay_", "Windows_x64_Setup.exe"],
   href_exclude_substrings=[".msix", ".zip", "Android", "macOS", "Linux", ".apk"],
   installer_extensions=[".exe"], windows_installer=True, run_installer=True)
_e("darwin", "22-音视频.json", "nipaplay",
   "NipaPlay Reload（macOS Apple Silicon dmg）", "音视频",
   "AimesSoft/NipaPlay-Reload",
   installer_markers_match_all=True,
   installer_markers=["NipaPlay_", "macOS_AppleSilicon.dmg"],
   href_exclude_substrings=["Intel", "Universal", ".pkg", ".zip", "Windows", "Linux", "Android"],
   installer_extensions=[".dmg"])
_e("linux", "22-音视频.json", "nipaplay",
   "NipaPlay Reload（Linux amd64 AppImage）", "音视频",
   "AimesSoft/NipaPlay-Reload",
   installer_markers_match_all=True,
   installer_markers=["NipaPlay-", "Linux-amd64.AppImage"],
   href_exclude_substrings=[".deb", ".rpm", ".tar.gz", "arm64", "Windows", "macOS", "Android"],
   installer_extensions=[".AppImage"])

_e("windows", "22-音视频.json", "fxsound",
   "FxSound（开源音频增强；Windows x64 Setup）", "音视频",
   "fxsound2/fxsound-app",
   installer_markers_match_all=True,
   installer_markers=["fxsound_setup", ".exe"],
   href_exclude_substrings=["arm64", ".msi", ".zip"],
   installer_extensions=[".exe"], windows_installer=True, run_installer=True)

_e("windows", "08-多媒体.json", "converseen",
   "Converseen（批量图片格式转换；Windows x64 Setup MSI）", "多媒体",
   "Faster3ck/Converseen",
   installer_markers_match_all=True,
   installer_markers=["Converseen-", "win64-setup.msi"],
   href_exclude_substrings=["portable", "win32", "macos", "AppImage", ".zsync"],
   installer_extensions=[".msi"], windows_installer=True, run_installer=True)
_e("linux", "08-多媒体.json", "converseen",
   "Converseen（Linux x86_64 AppImage）", "多媒体",
   "Faster3ck/Converseen",
   installer_markers_match_all=True,
   installer_markers=["Converseen-", "anylinux-x86_64.AppImage"],
   href_exclude_substrings=["aarch64", ".zsync", "win", "macos"],
   installer_extensions=[".AppImage"])


def _load_existing(plat: str) -> tuple[set[str], set[str]]:
    ids: set[str] = set()
    repos: set[str] = set()
    d = os.path.join(APPS, plat)
    if not os.path.isdir(d):
        return ids, repos
    for fn in os.listdir(d):
        if not fn.endswith(".json"):
            continue
        with open(os.path.join(d, fn), encoding="utf-8") as f:
            for item in json.load(f):
                if not isinstance(item, dict):
                    continue
                if item.get("id"):
                    ids.add(item["id"].strip())
                if item.get("repo_path"):
                    repos.add(item["repo_path"].lower())
    return ids, repos


def _merge(dry: bool) -> tuple[int, int]:
    added = skipped = 0
    plat_cache: dict[str, tuple[set[str], set[str]]] = {}
    for (plat, shard), apps in sorted(BATCH.items()):
        path = os.path.join(APPS, plat, shard)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = []
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        if plat not in plat_cache:
            plat_cache[plat] = _load_existing(plat)
        seen_ids, seen_repos = plat_cache[plat]
        file_ids = {(a.get("id") or "").strip() for a in data if isinstance(a, dict)}
        for app in apps:
            # skip vita3k if no windows asset (we'll remove from BATCH instead)
            if app.get("id") == "vita3k":
                skipped += 1
                continue
            rp = (app.get("repo_path") or "").lower()
            aid = (app.get("id") or "").strip()
            if aid in seen_ids or aid in file_ids or rp in seen_repos:
                skipped += 1
                continue
            data.append(app)
            seen_ids.add(aid)
            seen_repos.add(rp)
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
    # drop vita3k — continuous release currently no Windows zip in assets list
    for k in list(BATCH.keys()):
        BATCH[k] = [a for a in BATCH[k] if a.get("id") != "vita3k"]
        if not BATCH[k]:
            del BATCH[k]
    a, s = _merge(dry)
    print(f"{'dry-run' if dry else 'done'}: +{a} skip {s}")


if __name__ == "__main__":
    main()
