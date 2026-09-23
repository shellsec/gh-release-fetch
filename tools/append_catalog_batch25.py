#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Batch25：macked.app「开源软件」标签中有官方 GitHub Release 安装包的项目。"""
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
            "sha256", ".sig", ".asc", ".json", ".txt", ".md",
            "checksum", ".yml", ".blockmap", ".minisig", ".apk",
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


EX = [
    "source", "src.", "-src", "symbols", "debug", "pdb",
    "sha256", ".sig", ".asc", ".json", ".txt", ".md",
    "checksum", ".yml", ".blockmap", ".minisig", ".apk",
]


def _ex(*extra):
    return EX + list(extra)


SH_DL = "02-下载.json"
SH_MEDIA = "08-多媒体.json"
SH_SEC = "10-安全.json"
SH_TOOL = "11-工具.json"
SH_DEV = "12-开发.json"
SH_EFF = "13-效率.json"
SH_NOTE = "15-笔记.json"
SH_SYS = "16-系统.json"
SH_TERM = "17-终端.json"
SH_NET = "18-网络.json"
SH_REMOTE = "21-远程与协作.json"
SH_AV = "22-音视频.json"
SH_EDIT = "26-编辑器.json"

# --- OpenClip：PopClip 开源替代 ---
_e("darwin", SH_EFF, "openclip",
   "OpenClip（macOS 划词悬浮动作栏，PopClip 开源替代；Apple Silicon dmg）", "效率",
   "ganeshmshetty/openclip",
   installer_markers_match_all=True,
   installer_markers=["OpenClip-", ".dmg"],
   href_exclude_substrings=_ex(".zip"),
   installer_extensions=[".dmg"],
   aliases=["openclip", "OpenClip", "PopClip"])

# --- Stats：菜单栏系统监视 ---
_e("darwin", SH_SYS, "stats",
   "Stats（macOS 菜单栏系统监视器；dmg）", "系统",
   "exelban/stats",
   installer_markers_match_all=True,
   installer_markers=["Stats.dmg"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".dmg"],
   aliases=["stats", "Stats", "exelban"])

# --- CotEditor ---
_e("darwin", SH_EDIT, "coteditor",
   "CotEditor（macOS 开源文本编辑器；dmg）", "编辑器",
   "coteditor/CotEditor",
   installer_markers_match_all=True,
   installer_markers=["CotEditor_", ".dmg"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".dmg"],
   aliases=["coteditor", "CotEditor"])

# --- SwitchHosts ---
_e("windows", SH_NET, "switchhosts",
   "SwitchHosts（Hosts 快速切换；Windows x64 安装包）", "网络",
   "oldj/SwitchHosts",
   installer_markers_match_all=True,
   installer_markers=["SwitchHosts-", "windows-x64-setup.exe"],
   href_exclude_substrings=_ex("arm64", "x86", "linux", "mac", ".zip"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["switchhosts", "SwitchHosts"])
_e("darwin", SH_NET, "switchhosts",
   "SwitchHosts（Hosts 快速切换；macOS Apple Silicon dmg）", "网络",
   "oldj/SwitchHosts",
   installer_markers_match_all=True,
   installer_markers=["SwitchHosts-", "mac-aarch64.dmg"],
   href_exclude_substrings=_ex("x64", "universal", "windows", "linux"),
   installer_extensions=[".dmg"],
   aliases=["switchhosts", "SwitchHosts"])
_e("linux", SH_NET, "switchhosts",
   "SwitchHosts（Hosts 快速切换；Linux x64 AppImage）", "网络",
   "oldj/SwitchHosts",
   installer_markers_match_all=True,
   installer_markers=["SwitchHosts-", "linux-amd64.AppImage"],
   href_exclude_substrings=_ex("arm", "aarch64", "windows", "mac", ".deb", ".rpm"),
   installer_extensions=[".AppImage"],
   aliases=["switchhosts", "SwitchHosts"])

# --- IPTVnator ---
_e("windows", SH_AV, "iptvnator",
   "IPTVnator（跨平台 IPTV 播放器；Windows x64 安装包）", "音视频",
   "4gray/iptvnator",
   installer_markers_match_all=True,
   installer_markers=["iptvnator-", "windows-x64-setup.exe"],
   href_exclude_substrings=_ex("linux", "mac", ".zip"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["iptvnator", "IPTVnator"])
_e("darwin", SH_AV, "iptvnator",
   "IPTVnator（跨平台 IPTV 播放器；macOS Apple Silicon dmg）", "音视频",
   "4gray/iptvnator",
   installer_markers_match_all=True,
   installer_markers=["iptvnator-", "mac-arm64.dmg"],
   href_exclude_substrings=_ex("x64", "windows", "linux", ".zip"),
   installer_extensions=[".dmg"],
   aliases=["iptvnator", "IPTVnator"])
_e("linux", SH_AV, "iptvnator",
   "IPTVnator（跨平台 IPTV 播放器；Linux x64 deb）", "音视频",
   "4gray/iptvnator",
   installer_markers_match_all=True,
   installer_markers=["iptvnator-", "linux-amd64.deb"],
   href_exclude_substrings=_ex("arm64", "windows", "mac", ".snap", "AppImage"),
   installer_extensions=[".deb"],
   aliases=["iptvnator", "IPTVnator"])

# --- ABDownloadManager ---
_e("windows", SH_DL, "ab_download_manager",
   "ABDownloadManager（开源跨平台下载管理器；Windows x64 exe）", "下载",
   "amir1376/ab-download-manager",
   installer_markers_match_all=True,
   installer_markers=["ABDownloadManager_", "windows_x64.exe"],
   href_exclude_substrings=_ex("arm64", "linux", "mac", ".zip", ".md5", ".apk"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["abdownloadmanager", "ABDownloadManager", "AB Download Manager"])
_e("darwin", SH_DL, "ab_download_manager",
   "ABDownloadManager（开源跨平台下载管理器；macOS Apple Silicon dmg）", "下载",
   "amir1376/ab-download-manager",
   installer_markers_match_all=True,
   installer_markers=["ABDownloadManager_", "mac_arm64.dmg"],
   href_exclude_substrings=_ex("x64", "linux", "windows", ".tar.gz", ".md5"),
   installer_extensions=[".dmg"],
   aliases=["abdownloadmanager", "ABDownloadManager", "AB Download Manager"])
_e("linux", SH_DL, "ab_download_manager",
   "ABDownloadManager（开源跨平台下载管理器；Linux x64 tar.gz）", "下载",
   "amir1376/ab-download-manager",
   installer_markers_match_all=True,
   installer_markers=["ABDownloadManager_", "linux_x64.tar.gz"],
   href_exclude_substrings=_ex("arm64", "mac", "windows", ".md5", ".apk"),
   installer_extensions=[".tar.gz"],
   aliases=["abdownloadmanager", "ABDownloadManager", "AB Download Manager"])

# --- Easydict ---
_e("darwin", SH_EFF, "easydict",
   "Easydict（划词/截图翻译；macOS dmg）", "效率",
   "tisfeng/Easydict",
   installer_markers_match_all=True,
   installer_markers=["Easydict.dmg"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".dmg"],
   aliases=["easydict", "Easydict"])

# --- MiaoYan ---
_e("darwin", SH_NOTE, "miaoyan",
   "妙言 MiaoYan（macOS 原生 Markdown 编辑器；dmg）", "笔记",
   "tw93/MiaoYan",
   installer_markers_match_all=True,
   installer_markers=["MiaoYan.dmg"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".dmg"],
   aliases=["miaoyan", "MiaoYan", "妙言"])

# --- Maccy ---
_e("darwin", SH_TOOL, "maccy",
   "Maccy（macOS 原生剪贴板管理；app zip）", "工具",
   "p0deje/Maccy",
   installer_markers_match_all=True,
   installer_markers=["Maccy.app.zip"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".zip"],
   aliases=["maccy", "Maccy"])

# --- DockDoor ---
_e("darwin", SH_EFF, "dockdoor",
   "DockDoor（macOS Windows 风格窗口预览/切换；dmg）", "效率",
   "ejbills/DockDoor",
   installer_markers_match_all=True,
   installer_markers=["DockDoor.dmg"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".dmg"],
   aliases=["dockdoor", "DockDoor"])

# --- LuLu ---
_e("darwin", SH_SEC, "lulu",
   "LuLu（Objective-See macOS 开源防火墙；dmg）", "安全",
   "objective-see/LuLu",
   installer_markers_match_all=True,
   installer_markers=["LuLu_", ".dmg"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".dmg"],
   aliases=["lulu", "LuLu"])

# --- VutronMusic ---
_e("windows", SH_MEDIA, "vutronmusic",
   "VutronMusic（第三方网易云音乐播放器；Windows x64）", "多媒体",
   "stark81/VutronMusic",
   installer_markers_match_all=True,
   installer_markers=["VutronMusic-", "_win.exe"],
   href_exclude_substrings=_ex("arm64", "Portable", "linux", "mac", ".zip"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["vutronmusic", "VutronMusic"])
_e("darwin", SH_MEDIA, "vutronmusic",
   "VutronMusic（第三方网易云音乐播放器；macOS Apple Silicon dmg）", "多媒体",
   "stark81/VutronMusic",
   installer_markers_match_all=True,
   installer_markers=["VutronMusic-", "_mac_arm64.dmg"],
   href_exclude_substrings=_ex("x64", "linux", "win", ".zip"),
   installer_extensions=[".dmg"],
   aliases=["vutronmusic", "VutronMusic"])
_e("linux", SH_MEDIA, "vutronmusic",
   "VutronMusic（第三方网易云音乐播放器；Linux x64 deb）", "多媒体",
   "stark81/VutronMusic",
   installer_markers_match_all=True,
   installer_markers=["VutronMusic-", "_linux_amd64.deb"],
   href_exclude_substrings=_ex("arm64", "aarch64", "mac", "win", "AppImage", ".rpm"),
   installer_extensions=[".deb"],
   aliases=["vutronmusic", "VutronMusic"])

# --- EcoPaste ---
_e("windows", SH_TOOL, "ecopaste",
   "EcoPaste（开源剪贴板管理；Windows x64 安装包）", "工具",
   "EcoPasteHub/EcoPaste",
   installer_markers_match_all=True,
   installer_markers=["EcoPaste_", "_x64-setup.exe"],
   href_exclude_substrings=_ex("arm64", ".sig", "linux", "dmg", ".zip"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["ecopaste", "EcoPaste"])
_e("darwin", SH_TOOL, "ecopaste",
   "EcoPaste（开源剪贴板管理；macOS Apple Silicon dmg）", "工具",
   "EcoPasteHub/EcoPaste",
   installer_markers_match_all=True,
   installer_markers=["EcoPaste_", "_aarch64.dmg"],
   href_exclude_substrings=_ex("x64", "windows", "exe", ".tar.gz"),
   installer_extensions=[".dmg"],
   aliases=["ecopaste", "EcoPaste"])

# --- Pika ---
_e("darwin", SH_TOOL, "pika",
   "Pika（macOS 菜单栏取色；dmg）", "工具",
   "superhighfives/pika",
   installer_markers_match_all=True,
   installer_markers=["Pika-", ".dmg"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".dmg"],
   aliases=["pika", "Pika"])

# --- Keka ---
_e("darwin", SH_TOOL, "keka",
   "Keka（macOS 压缩/解压；dmg）", "工具",
   "aonez/Keka",
   installer_markers_match_all=True,
   installer_markers=["Keka-", ".dmg"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".dmg"],
   aliases=["keka", "Keka"])

# --- Reminders MenuBar ---
_e("darwin", SH_EFF, "reminders_menubar",
   "Reminders MenuBar（菜单栏管理提醒事项；dmg）", "效率",
   "DamascenoRafael/reminders-menubar",
   installer_markers_match_all=True,
   installer_markers=["Reminders-MenuBar.dmg"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".dmg"],
   aliases=["reminders-menubar", "Reminders MenuBar"])

# --- Kando ---
_e("windows", SH_EFF, "kando",
   "Kando（开源饼状菜单；Windows x64 安装包）", "效率",
   "kando-menu/kando",
   installer_markers_match_all=True,
   installer_markers=["Kando-", "Setup-x64.exe"],
   href_exclude_substrings=_ex("arm64", "darwin", "linux", "AppImage", ".rpm", ".zip"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["kando", "Kando"])
_e("darwin", SH_EFF, "kando",
   "Kando（开源饼状菜单；macOS Apple Silicon dmg）", "效率",
   "kando-menu/kando",
   installer_markers_match_all=True,
   installer_markers=["Kando-", "-arm64.dmg"],
   href_exclude_substrings=_ex("x64", "windows", "linux", "Setup", ".zip", "darwin-"),
   installer_extensions=[".dmg"],
   aliases=["kando", "Kando"])
_e("linux", SH_EFF, "kando",
   "Kando（开源饼状菜单；Linux x64 AppImage）", "效率",
   "kando-menu/kando",
   installer_markers_match_all=True,
   installer_markers=["Kando-", "-x86_64.AppImage"],
   href_exclude_substrings=_ex("arm64", "aarch64", "windows", "darwin", ".rpm", ".dmg"),
   installer_extensions=[".AppImage"],
   aliases=["kando", "Kando"])

# --- Fluent Reader ---
_e("windows", SH_NET, "fluent_reader",
   "Fluent Reader（开源 RSS 阅读器；Windows x64 安装包）", "网络",
   "yang991178/fluent-reader",
   installer_markers_match_all=True,
   installer_markers=["Fluent.Reader.Setup.", ".x64.exe"],
   href_exclude_substrings=_ex("x86", "linux", "dmg", ".zip"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["fluent reader", "Fluent Reader", "fluent-reader"])
_e("darwin", SH_NET, "fluent_reader",
   "Fluent Reader（开源 RSS 阅读器；macOS dmg）", "网络",
   "yang991178/fluent-reader",
   installer_markers_match_all=True,
   installer_markers=["Fluent.Reader.", ".dmg"],
   href_exclude_substrings=_ex("Setup", "windows", "AppImage", ".zip"),
   installer_extensions=[".dmg"],
   aliases=["fluent reader", "Fluent Reader", "fluent-reader"])
_e("linux", SH_NET, "fluent_reader",
   "Fluent Reader（开源 RSS 阅读器；Linux AppImage）", "网络",
   "yang991178/fluent-reader",
   installer_markers_match_all=True,
   installer_markers=["Fluent.Reader.", ".AppImage"],
   href_exclude_substrings=_ex("windows", "Setup", "dmg"),
   installer_extensions=[".AppImage"],
   aliases=["fluent reader", "Fluent Reader", "fluent-reader"])

# --- Psst ---
_e("windows", SH_MEDIA, "psst",
   "Psst（轻量 Spotify 客户端；Windows exe）", "多媒体",
   "jpochyla/psst",
   installer_markers_match_all=True,
   installer_markers=["Psst.exe"],
   href_exclude_substrings=_ex("linux", "dmg", ".deb"),
   installer_extensions=[".exe"],
   aliases=["psst", "Psst"])
_e("darwin", SH_MEDIA, "psst",
   "Psst（轻量 Spotify 客户端；macOS dmg）", "多媒体",
   "jpochyla/psst",
   installer_markers_match_all=True,
   installer_markers=["Psst.dmg"],
   href_exclude_substrings=_ex("linux", "exe", ".deb"),
   installer_extensions=[".dmg"],
   aliases=["psst", "Psst"])
_e("linux", SH_MEDIA, "psst",
   "Psst（轻量 Spotify 客户端；Linux amd64 deb）", "多媒体",
   "jpochyla/psst",
   installer_markers_match_all=True,
   installer_markers=["psst-amd64.deb"],
   href_exclude_substrings=_ex("arm64", "windows", "dmg"),
   installer_extensions=[".deb"],
   aliases=["psst", "Psst"])

# --- PicList ---
_e("windows", SH_EFF, "piclist",
   "PicList（开源图床/图床管理，PicGo 增强；Windows x64 安装包）", "效率",
   "Kuingsmile/PicList",
   installer_markers_match_all=True,
   installer_markers=["PicList-Setup-", "-x64.exe"],
   href_exclude_substrings=_ex("arm64", "linux", "mac", "dmg", ".yml"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["piclist", "PicList"])
_e("darwin", SH_EFF, "piclist",
   "PicList（开源图床/图床管理；macOS Apple Silicon dmg）", "效率",
   "Kuingsmile/PicList",
   installer_markers_match_all=True,
   installer_markers=["PicList-", "-arm64.dmg"],
   href_exclude_substrings=_ex("x64", "windows", "linux", "Setup"),
   installer_extensions=[".dmg"],
   aliases=["piclist", "PicList"])
_e("linux", SH_EFF, "piclist",
   "PicList（开源图床/图床管理；Linux x64 deb）", "效率",
   "Kuingsmile/PicList",
   installer_markers_match_all=True,
   installer_markers=["PicList-", "-amd64.deb"],
   href_exclude_substrings=_ex("arm64", "aarch64", "windows", "mac", "AppImage", ".rpm"),
   installer_extensions=[".deb"],
   aliases=["piclist", "PicList"])

# --- CodeEdit ---
_e("darwin", SH_EDIT, "codeedit",
   "CodeEdit（macOS 原生代码编辑器；dmg）", "编辑器",
   "CodeEditApp/CodeEdit",
   installer_markers_match_all=True,
   installer_markers=["CodeEdit.dmg"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".dmg"],
   aliases=["codeedit", "CodeEdit"])

# --- Hidden Bar ---
_e("darwin", SH_EFF, "hidden_bar",
   "Hidden Bar（菜单栏图标隐藏；macos zip）", "效率",
   "dwarvesf/hidden",
   installer_markers_match_all=True,
   installer_markers=["Hidden-Bar-", "-macos.zip"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".zip"],
   aliases=["hidden bar", "Hidden Bar", "hiddenbar"])

# --- Battery（充电限制） ---
_e("darwin", SH_SYS, "battery_limiter",
   "Battery（限制充电保护电池，AlDente 同类；macOS Apple Silicon dmg）", "系统",
   "actuallymentor/battery",
   installer_markers_match_all=True,
   installer_markers=["battery-", "-mac-arm64.dmg"],
   href_exclude_substrings=_ex("x64", ".zip", "windows", "linux"),
   installer_extensions=[".dmg"],
   aliases=["battery", "Battery", "充电限制"])

# --- FlyEnv / PhpWebStudy ---
_e("windows", SH_DEV, "flyenv",
   "FlyEnv（原 PhpWebStudy，本地开发环境；Windows 安装包）", "开发",
   "xpf0000/PhpWebStudy",
   installer_markers_match_all=True,
   installer_markers=["FlyEnv-Setup-", ".exe"],
   href_exclude_substrings=_ex("Portable", "linux", "mac", "arm64", ".blockmap"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["flyenv", "FlyEnv", "PhpWebStudy"])
_e("darwin", SH_DEV, "flyenv",
   "FlyEnv（原 PhpWebStudy，本地开发环境；macOS Apple Silicon dmg）", "开发",
   "xpf0000/PhpWebStudy",
   installer_markers_match_all=True,
   installer_markers=["FlyEnv-", "-arm64.dmg"],
   href_exclude_substrings=_ex("x64", "windows", "linux", ".zip", ".deb", ".rpm"),
   installer_extensions=[".dmg"],
   aliases=["flyenv", "FlyEnv", "PhpWebStudy"])
_e("linux", SH_DEV, "flyenv",
   "FlyEnv（原 PhpWebStudy，本地开发环境；Linux x64 deb）", "开发",
   "xpf0000/PhpWebStudy",
   installer_markers_match_all=True,
   installer_markers=["FlyEnv-", "-x64.deb"],
   href_exclude_substrings=_ex("arm64", "windows", "mac", ".rpm", ".dmg"),
   installer_extensions=[".deb"],
   aliases=["flyenv", "FlyEnv", "PhpWebStudy"])

# --- Finicky ---
_e("darwin", SH_NET, "finicky",
   "Finicky（按规则选择打开 URL 的浏览器；dmg）", "网络",
   "johnste/finicky",
   installer_markers_match_all=True,
   installer_markers=["Finicky.dmg"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".dmg"],
   aliases=["finicky", "Finicky"])

# --- Pearcleaner ---
_e("darwin", SH_SYS, "pearcleaner",
   "Pearcleaner（开源应用卸载/清理；dmg）", "系统",
   "alienator88/Pearcleaner",
   installer_markers_match_all=True,
   installer_markers=["Pearcleaner.dmg"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".dmg"],
   aliases=["pearcleaner", "Pearcleaner"])

# --- Boring Notch ---
_e("darwin", SH_EFF, "boring_notch",
   "Boring Notch（MacBook 刘海动态岛控制中心；dmg）", "效率",
   "TheBoredTeam/boring.notch",
   installer_markers_match_all=True,
   installer_markers=["boringNotch.dmg"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".dmg"],
   aliases=["boring notch", "Boring Notch", "boringNotch"])

# --- Lan Mouse ---
_e("windows", SH_REMOTE, "lan_mouse",
   "Lan Mouse（跨平台键鼠共享；Windows x64 zip）", "远程与协作",
   "feschber/lan-mouse",
   installer_markers_match_all=True,
   installer_markers=["lan-mouse-windows-x86_64.zip"],
   href_exclude_substrings=_ex("linux", "macos", "arm64"),
   installer_extensions=[".zip"],
   aliases=["lan mouse", "Lan Mouse", "lan-mouse"])
_e("darwin", SH_REMOTE, "lan_mouse",
   "Lan Mouse（跨平台键鼠共享；macOS Apple Silicon zip）", "远程与协作",
   "feschber/lan-mouse",
   installer_markers_match_all=True,
   installer_markers=["lan-mouse-macos-arm64.zip"],
   href_exclude_substrings=_ex("intel", "linux", "windows"),
   installer_extensions=[".zip"],
   aliases=["lan mouse", "Lan Mouse", "lan-mouse"])

# --- YesPlayMusic ---
_e("windows", SH_MEDIA, "yesplaymusic",
   "YesPlayMusic（第三方网易云音乐播放器；Windows 安装包）", "多媒体",
   "qier222/YesPlayMusic",
   installer_markers_match_all=True,
   installer_markers=["YesPlayMusic-Setup-", ".exe"],
   href_exclude_substrings=_ex("linux", "mac", "AppImage", ".blockmap"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["yesplaymusic", "YesPlayMusic"])
_e("darwin", SH_MEDIA, "yesplaymusic",
   "YesPlayMusic（第三方网易云音乐播放器；macOS Apple Silicon dmg）", "多媒体",
   "qier222/YesPlayMusic",
   installer_markers_match_all=True,
   installer_markers=["YesPlayMusic-mac-", "-arm64.dmg"],
   href_exclude_substrings=_ex("universal", "x64", "windows", "linux", ".tar.gz"),
   installer_extensions=[".dmg"],
   aliases=["yesplaymusic", "YesPlayMusic"])
_e("linux", SH_MEDIA, "yesplaymusic",
   "YesPlayMusic（第三方网易云音乐播放器；Linux AppImage）", "多媒体",
   "qier222/YesPlayMusic",
   installer_markers_match_all=True,
   installer_markers=["YesPlayMusic-", ".AppImage"],
   href_exclude_substrings=_ex("windows", "mac", ".deb", ".rpm", ".yml"),
   installer_extensions=[".AppImage"],
   aliases=["yesplaymusic", "YesPlayMusic"])

# --- UTM ---
_e("darwin", SH_SYS, "utm",
   "UTM（macOS 开源虚拟机；dmg）", "系统",
   "utmapp/UTM",
   installer_markers_match_all=True,
   installer_markers=["UTM.dmg"],
   href_exclude_substrings=_ex(".deb", "SE", "Remote"),
   installer_extensions=[".dmg"],
   aliases=["utm", "UTM"])

# --- Mac Mouse Fix ---
_e("darwin", SH_SYS, "mac_mouse_fix",
   "Mac Mouse Fix（鼠标平滑滚动/按键；app zip）", "系统",
   "noah-nuebling/mac-mouse-fix",
   installer_markers_match_all=True,
   installer_markers=["MacMouseFixApp.zip"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".zip"],
   aliases=["mac mouse fix", "Mac Mouse Fix"])

# --- OnlySwitch ---
_e("darwin", SH_EFF, "onlyswitch",
   "OnlySwitch（菜单栏系统开关合集；dmg）", "效率",
   "jacklandrin/OnlySwitch",
   installer_markers_match_all=True,
   installer_markers=["OnlySwitch.dmg"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".dmg"],
   aliases=["onlyswitch", "OnlySwitch"])

# --- Handy ---
_e("windows", SH_EFF, "handy",
   "Handy（开源语音输入；Windows x64 安装包）", "效率",
   "cjpais/Handy",
   installer_markers_match_all=True,
   installer_markers=["Handy_", "_x64-setup.exe"],
   href_exclude_substrings=_ex("arm64", "linux", "dmg", ".msi", ".sig"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["handy", "Handy"])
_e("darwin", SH_EFF, "handy",
   "Handy（开源语音输入；macOS Apple Silicon dmg）", "效率",
   "cjpais/Handy",
   installer_markers_match_all=True,
   installer_markers=["Handy_", "_aarch64.dmg"],
   href_exclude_substrings=_ex("x64", "windows", "linux", ".tar.gz"),
   installer_extensions=[".dmg"],
   aliases=["handy", "Handy"])
_e("linux", SH_EFF, "handy",
   "Handy（开源语音输入；Linux x64 AppImage）", "效率",
   "cjpais/Handy",
   installer_markers_match_all=True,
   installer_markers=["Handy_", "_amd64.AppImage"],
   href_exclude_substrings=_ex("aarch64", "arm64", "windows", "dmg", ".deb", ".rpm", ".sig"),
   installer_extensions=[".AppImage"],
   aliases=["handy", "Handy"])

# --- Pot ---
_e("windows", SH_EFF, "pot",
   "Pot（划词翻译/OCR；Windows x64 安装包）", "效率",
   "pot-app/pot-desktop",
   installer_markers_match_all=True,
   installer_markers=["pot_", "_x64-setup.exe"],
   href_exclude_substrings=_ex("arm64", "x86", "linux", "dmg", "webview2", ".zip"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["pot", "Pot", "pot-desktop"])
_e("darwin", SH_EFF, "pot",
   "Pot（划词翻译/OCR；macOS Apple Silicon dmg）", "效率",
   "pot-app/pot-desktop",
   installer_markers_match_all=True,
   installer_markers=["pot_", "_aarch64.dmg"],
   href_exclude_substrings=_ex("x64", "windows", "linux", ".tar.gz"),
   installer_extensions=[".dmg"],
   aliases=["pot", "Pot", "pot-desktop"])
_e("linux", SH_EFF, "pot",
   "Pot（划词翻译/OCR；Linux x64 AppImage）", "效率",
   "pot-app/pot-desktop",
   installer_markers_match_all=True,
   installer_markers=["pot_", "_amd64.AppImage"],
   href_exclude_substrings=_ex("arm", "windows", "dmg", ".deb", ".rpm", ".tar.gz"),
   installer_extensions=[".AppImage"],
   aliases=["pot", "Pot", "pot-desktop"])

# --- LinearMouse ---
_e("darwin", SH_SYS, "linearmouse",
   "LinearMouse（鼠标/触控板调校；dmg）", "系统",
   "linearmouse/linearmouse",
   installer_markers_match_all=True,
   installer_markers=["LinearMouse.dmg"],
   href_exclude_substrings=_ex("dSYM"),
   installer_extensions=[".dmg"],
   aliases=["linearmouse", "LinearMouse"])

# --- MonitorControl ---
_e("darwin", SH_SYS, "monitorcontrol",
   "MonitorControl（外接显示器亮度/音量；dmg）", "系统",
   "MonitorControl/MonitorControl",
   installer_markers_match_all=True,
   installer_markers=["MonitorControl.", ".dmg"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".dmg"],
   aliases=["monitorcontrol", "MonitorControl"])

# --- AirBattery ---
_e("darwin", SH_SYS, "airbattery",
   "AirBattery（Apple 设备电量显示；dmg）", "系统",
   "lihaoyun6/AirBattery",
   installer_markers_match_all=True,
   installer_markers=["AirBattery_v", ".dmg"],
   href_exclude_substrings=_ex(".delta"),
   installer_extensions=[".dmg"],
   aliases=["airbattery", "AirBattery"])

# --- QuickRecorder ---
_e("darwin", SH_MEDIA, "quickrecorder",
   "QuickRecorder（开源轻量屏幕录制；dmg）", "多媒体",
   "lihaoyun6/QuickRecorder",
   installer_markers_match_all=True,
   installer_markers=["QuickRecorder_v", ".dmg"],
   href_exclude_substrings=_ex(".delta"),
   installer_extensions=[".dmg"],
   aliases=["quickrecorder", "QuickRecorder"])

# --- Hyper ---
_e("windows", SH_TERM, "hyper",
   "Hyper（Electron 终端；Windows 安装包）", "终端",
   "vercel/hyper",
   installer_markers_match_all=True,
   installer_markers=["Hyper-Setup-", ".exe"],
   href_exclude_substrings=_ex("linux", "mac", "AppImage", ".blockmap"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["hyper", "Hyper"])
_e("darwin", SH_TERM, "hyper",
   "Hyper（Electron 终端；macOS Apple Silicon dmg）", "终端",
   "vercel/hyper",
   installer_markers_match_all=True,
   installer_markers=["Hyper-", "-mac-arm64.dmg"],
   href_exclude_substrings=_ex("x64", "windows", "linux", ".zip"),
   installer_extensions=[".dmg"],
   aliases=["hyper", "Hyper"])
_e("linux", SH_TERM, "hyper",
   "Hyper（Electron 终端；Linux x64 AppImage）", "终端",
   "vercel/hyper",
   installer_markers_match_all=True,
   installer_markers=["Hyper-", ".AppImage"],
   href_exclude_substrings=_ex("arm64", "windows", "mac", ".deb", ".rpm"),
   installer_extensions=[".AppImage"],
   aliases=["hyper", "Hyper"])


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
        data = json.load(open(path, encoding="utf-8")) if os.path.isfile(path) else []
        if plat not in plat_cache:
            plat_cache[plat] = _load_existing(plat)
        seen_ids, seen_repos = plat_cache[plat]
        file_ids = {(a.get("id") or "").strip() for a in data if isinstance(a, dict)}
        for app in apps:
            rp = (app.get("repo_path") or "").lower()
            aid = (app.get("id") or "").strip()
            if aid in seen_ids or aid in file_ids or rp in seen_repos:
                skipped += 1
                print(f"skip {plat}/{aid} ({rp})")
                continue
            data.append(app)
            seen_ids.add(aid)
            seen_repos.add(rp)
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
