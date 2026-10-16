#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Batch33：macked.app「开源软件」标签补漏，仅官方 GitHub Release 安装包。"""
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


SH_AI = "01-AI.json"
SH_MEDIA = "08-多媒体.json"
SH_TOOL = "11-工具.json"
SH_DEV = "12-开发.json"
SH_EFF = "13-效率.json"
SH_BAK = "07-备份.json"
SH_SYS = "16-系统.json"
SH_NET = "18-网络.json"
SH_AV = "22-音视频.json"
SH_DB = "23-数据库.json"
SH_OBS = "25-可观测.json"
SH_FIN = "27-金融与股票.json"
SH_LAN = "29-局域网文件共享.json"
SH_PROXY = "30-代理与隧道.json"

# --- HotkeyClash ---
_e("darwin", SH_TOOL, "hotkeyclash",
   "HotkeyClash（macOS 快捷键冲突检测；dmg）", "工具",
   "Wunderlandmedia/HotkeyClash",
   installer_markers_match_all=True,
   installer_markers=["HotkeyClash-", ".dmg"],
   href_exclude_substrings=_ex(".zip"),
   installer_extensions=[".dmg"],
   aliases=["hotkeyclash", "HotkeyClash"])

# --- WinMux ---
_e("darwin", SH_EFF, "winmux",
   "WinMux（macOS 项目工作区窗口管理；zip）", "效率",
   "ZimengXiong/WinMux",
   installer_markers_match_all=True,
   installer_markers=["WinMux-", ".zip"],
   href_exclude_substrings=_ex("appcast"),
   installer_extensions=[".zip"],
   aliases=["winmux", "WinMux"])

# --- Loop ---
_e("darwin", SH_EFF, "loop",
   "Loop（macOS 轻量窗口管理；app zip）", "效率",
   "mrkai77/Loop",
   installer_markers_match_all=True,
   installer_markers=["Loop.zip"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".zip"],
   aliases=["loop", "Loop"])

# --- Swift Shift ---
_e("darwin", SH_EFF, "swift_shift",
   "Swift Shift（按住修饰键拖移窗口；app zip）", "效率",
   "pablopunk/SwiftShift",
   installer_markers_match_all=True,
   installer_markers=["SwiftShift.zip"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".zip"],
   aliases=["swift shift", "Swift Shift", "SwiftShift"])

# --- Keyboard Cowboy ---
_e("darwin", SH_EFF, "keyboard_cowboy",
   "Keyboard Cowboy（macOS 快捷键工作流；dmg）", "效率",
   "zenangst/KeyboardCowboy",
   installer_markers_match_all=True,
   installer_markers=["Keyboard.Cowboy.", ".dmg"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".dmg"],
   aliases=["keyboard cowboy", "Keyboard Cowboy", "KeyboardCowboy"])

# --- Mos ---
_e("darwin", SH_SYS, "mos",
   "Mos（鼠标平滑滚动；app zip）", "系统",
   "Caldis/Mos",
   installer_markers_match_all=True,
   installer_markers=["Mos.Versions.", ".zip"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".zip"],
   aliases=["mos", "Mos"])

# --- AlDente ---
_e("darwin", SH_SYS, "aldente",
   "AlDente（限制最大充电量；dmg）", "系统",
   "AppHouseKitchen/AlDente-Charge-Limiter",
   installer_markers_match_all=True,
   installer_markers=["AlDente.dmg"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".dmg"],
   aliases=["aldente", "AlDente"])

# --- MountMate ---
_e("darwin", SH_SYS, "mountmate",
   "MountMate（外置磁盘挂载管理；dmg）", "系统",
   "homielab/mountmate",
   installer_markers_match_all=True,
   installer_markers=["MountMate_", ".dmg"],
   href_exclude_substrings=_ex(".zip"),
   installer_extensions=[".dmg"],
   aliases=["mountmate", "MountMate"])

# --- Sloth ---
_e("darwin", SH_SYS, "sloth",
   "Sloth（lsof 图形界面，查看打开的文件与套接字；zip）", "系统",
   "sveinbjornt/Sloth",
   installer_markers_match_all=True,
   installer_markers=["sloth-", ".zip"],
   href_exclude_substrings=_ex(".src"),
   installer_extensions=[".zip"],
   aliases=["sloth", "Sloth"])

# --- Sequel Ace ---
_e("darwin", SH_DB, "sequel_ace",
   "Sequel Ace（MySQL/MariaDB 客户端；app zip）", "数据库",
   "Sequel-Ace/Sequel-Ace",
   installer_markers_match_all=True,
   installer_markers=["Sequel-Ace-", ".zip"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".zip"],
   aliases=["sequel ace", "Sequel Ace", "Sequel-Ace"])

# --- Another Redis Desktop Manager ---
_e("windows", SH_DB, "another_redis_desktop_manager",
   "Another Redis Desktop Manager（Redis 桌面客户端；Windows x64）", "数据库",
   "qishibo/AnotherRedisDesktopManager",
   installer_markers_match_all=True,
   installer_markers=["Another-Redis-Desktop-Manager-win-", "-x64.exe"],
   href_exclude_substrings=_ex("arm64", "linux", "mac", ".zip"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["another redis desktop manager", "Another Redis Desktop Manager"])
_e("darwin", SH_DB, "another_redis_desktop_manager",
   "Another Redis Desktop Manager（Redis 桌面客户端；macOS Apple Silicon dmg）", "数据库",
   "qishibo/AnotherRedisDesktopManager",
   installer_markers_match_all=True,
   installer_markers=["Another-Redis-Desktop-Manager-mac-", "-arm64.dmg"],
   href_exclude_substrings=_ex("x64", "windows", "linux", ".zip"),
   installer_extensions=[".dmg"],
   aliases=["another redis desktop manager", "Another Redis Desktop Manager"])
_e("linux", SH_DB, "another_redis_desktop_manager",
   "Another Redis Desktop Manager（Redis 桌面客户端；Linux x64 AppImage）", "数据库",
   "qishibo/AnotherRedisDesktopManager",
   installer_markers_match_all=True,
   installer_markers=["Another-Redis-Desktop-Manager-linux-", "-x86_64.AppImage"],
   href_exclude_substrings=_ex("arm64", "windows", "mac", ".deb"),
   installer_extensions=[".AppImage"],
   aliases=["another redis desktop manager", "Another Redis Desktop Manager"])

# --- NetNewsWire ---
_e("darwin", SH_NET, "netnewswire",
   "NetNewsWire（macOS RSS 阅读器；app zip）", "网络",
   "Ranchero-Software/NetNewsWire",
   installer_markers_match_all=True,
   installer_markers=["NetNewsWire", ".zip"],
   href_exclude_substrings=_ex("ios"),
   installer_extensions=[".zip"],
   aliases=["netnewswire", "NetNewsWire"])

# --- Browserosaurus ---
_e("darwin", SH_NET, "browserosaurus",
   "Browserosaurus（按规则选择浏览器；Apple Silicon zip）", "网络",
   "will-stone/browserosaurus",
   installer_markers_match_all=True,
   installer_markers=["Browserosaurus-darwin-arm64-", ".zip"],
   href_exclude_substrings=_ex("x64"),
   installer_extensions=[".zip"],
   aliases=["browserosaurus", "Browserosaurus"])

# --- Sniffnet ---
_e("windows", SH_OBS, "sniffnet",
   "Sniffnet（网络流量监控；Windows x64 msi）", "可观测",
   "GyulyVGC/sniffnet",
   installer_markers_match_all=True,
   installer_markers=["Sniffnet_Windows_x64.msi"],
   href_exclude_substrings=_ex("arm64", "x86.msi", "linux", "mac"),
   installer_extensions=[".msi"], windows_installer=True, run_installer=True,
   aliases=["sniffnet", "Sniffnet"])
_e("darwin", SH_OBS, "sniffnet",
   "Sniffnet（网络流量监控；macOS Apple Silicon dmg）", "可观测",
   "GyulyVGC/sniffnet",
   installer_markers_match_all=True,
   installer_markers=["Sniffnet_macOS_AppleSilicon.dmg"],
   href_exclude_substrings=_ex("Intel", "windows", "linux"),
   installer_extensions=[".dmg"],
   aliases=["sniffnet", "Sniffnet"])
_e("linux", SH_OBS, "sniffnet",
   "Sniffnet（网络流量监控；Linux amd64 deb）", "可观测",
   "GyulyVGC/sniffnet",
   installer_markers_match_all=True,
   installer_markers=["Sniffnet_LinuxDEB_amd64.deb"],
   href_exclude_substrings=_ex("arm64", "armhf", "i386", "AppImage", "rpm", "windows", "mac"),
   installer_extensions=[".deb"],
   aliases=["sniffnet", "Sniffnet"])

# --- Double Commander ---
_e("windows", SH_TOOL, "double_commander",
   "Double Commander（双栏文件管理；Windows x64 安装包）", "工具",
   "doublecmd/doublecmd",
   installer_markers_match_all=True,
   installer_markers=["doublecmd-", "x86_64-win64.exe"],
   href_exclude_substrings=_ex("i386", "linux", "cocoa", ".msi", ".zip"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["double commander", "Double Commander", "doublecmd"])
_e("darwin", SH_TOOL, "double_commander",
   "Double Commander（双栏文件管理；macOS Apple Silicon dmg）", "工具",
   "doublecmd/doublecmd",
   installer_markers_match_all=True,
   installer_markers=["doublecmd-", "cocoa.aarch64.dmg"],
   href_exclude_substrings=_ex("x86_64", "windows", "gtk", "qt"),
   installer_extensions=[".dmg"],
   aliases=["double commander", "Double Commander", "doublecmd"])
_e("linux", SH_TOOL, "double_commander",
   "Double Commander（双栏文件管理；Linux x64 Qt6 tar.xz）", "工具",
   "doublecmd/doublecmd",
   installer_markers_match_all=True,
   installer_markers=["doublecmd-", "qt6.x86_64.tar.xz"],
   href_exclude_substrings=_ex("aarch64", "i386", "gtk", "windows", "cocoa", "AppImage"),
   installer_extensions=[".tar.xz"],
   aliases=["double commander", "Double Commander", "doublecmd"])

# --- TRex ---
_e("darwin", SH_TOOL, "trex",
   "TRex（菜单栏离线 OCR；zip）", "工具",
   "amebalabs/TRex",
   installer_markers_match_all=True,
   installer_markers=["TRex-", ".zip"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".zip"],
   aliases=["trex", "TRex"])

# --- WailBrew ---
_e("darwin", SH_TOOL, "wailbrew",
   "WailBrew（Homebrew 图形界面；zip）", "工具",
   "wickenico/WailBrew",
   installer_markers_match_all=True,
   installer_markers=["wailbrew-", ".zip"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".zip"],
   aliases=["wailbrew", "WailBrew"])

# --- SourceCodeSyntaxHighlight ---
_e("darwin", SH_TOOL, "sourcecode_syntax_highlight",
   "SourceCodeSyntaxHighlight（QuickLook 源代码高亮；zip）", "工具",
   "sbarex/SourceCodeSyntaxHighlight",
   installer_markers_match_all=True,
   installer_markers=["Syntax.Highlight.zip"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".zip"],
   aliases=["sourcecode syntax highlight", "Syntax Highlight", "SourceCodeSyntaxHighlight"])

# --- GitUp ---
_e("darwin", SH_DEV, "gitup",
   "GitUp（macOS Git 客户端；zip）", "开发",
   "git-up/GitUp",
   installer_markers_match_all=True,
   installer_markers=["GitUp.zip"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".zip"],
   aliases=["gitup", "GitUp"])

# --- PHP Monitor ---
_e("darwin", SH_DEV, "phpmon",
   "PHP Monitor（macOS PHP 版本切换；zip）", "开发",
   "nicoverbruggen/phpmon",
   installer_markers_match_all=True,
   installer_markers=["phpmon.zip"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".zip"],
   aliases=["phpmon", "PHP Monitor", "php monitor"])

# --- MiniSim ---
_e("darwin", SH_DEV, "minisim",
   "MiniSim（菜单栏模拟器启动器；app zip）", "开发",
   "okwasniewski/MiniSim",
   installer_markers_match_all=True,
   installer_markers=["MiniSim.app.zip"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".zip"],
   aliases=["minisim", "MiniSim"])

# --- FlowDown ---
_e("darwin", SH_AI, "flowdown",
   "FlowDown（macOS 多模型 AI 聊天；zip）", "AI",
   "Lakr233/FlowDown",
   installer_markers_match_all=True,
   installer_markers=["FlowDown-", ".zip"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".zip"],
   aliases=["flowdown", "FlowDown"])

# --- RsyncUI ---
_e("darwin", SH_BAK, "rsyncui",
   "RsyncUI（Rsync 图形界面；Apple Silicon dmg）", "备份",
   "rsyncOSX/RsyncUI",
   installer_markers_match_all=True,
   installer_markers=["RsyncUI.", "arm64.dmg"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".dmg"],
   aliases=["rsyncui", "RsyncUI"])

# --- NearDrop ---
_e("darwin", SH_LAN, "neardrop",
   "NearDrop（macOS 接收 Android Quick Share；app zip）", "局域网文件共享",
   "grishka/NearDrop",
   installer_markers_match_all=True,
   installer_markers=["NearDrop.app.zip"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".zip"],
   aliases=["neardrop", "NearDrop"])

# --- Background Music ---
_e("darwin", SH_AV, "background_music",
   "Background Music（按应用调节音量；pkg）", "音视频",
   "kyleneideck/BackgroundMusic",
   installer_markers_match_all=True,
   installer_markers=["BackgroundMusic-", ".pkg"],
   href_exclude_substrings=_ex("build-artifacts"),
   installer_extensions=[".pkg"],
   aliases=["background music", "Background Music", "BackgroundMusic"])

# --- Aerial ---
_e("darwin", SH_MEDIA, "aerial",
   "Aerial（苹果风格动态屏保；saver zip）", "多媒体",
   "JohnCoates/Aerial",
   installer_markers_match_all=True,
   installer_markers=["Aerial.saver.zip"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".zip"],
   aliases=["aerial", "Aerial"])

# --- Fishing Funds ---
_e("windows", SH_FIN, "fishing_funds",
   "Fishing Funds（基金涨跌状态栏；Windows 安装包）", "金融与股票",
   "1zilc/fishing-funds",
   installer_markers_match_all=True,
   installer_markers=["Fishing-Funds-Setup-", ".exe"],
   href_exclude_substrings=_ex("linux", "dmg", "AppImage"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["fishing funds", "Fishing Funds"])
_e("darwin", SH_FIN, "fishing_funds",
   "Fishing Funds（基金涨跌状态栏；macOS Apple Silicon dmg）", "金融与股票",
   "1zilc/fishing-funds",
   installer_markers_match_all=True,
   installer_markers=["Fishing-Funds-", "-arm64.dmg"],
   href_exclude_substrings=_ex("Setup", "windows", "AppImage"),
   installer_extensions=[".dmg"],
   aliases=["fishing funds", "Fishing Funds"])
_e("linux", SH_FIN, "fishing_funds",
   "Fishing Funds（基金涨跌状态栏；Linux x64 AppImage）", "金融与股票",
   "1zilc/fishing-funds",
   installer_markers_match_all=True,
   installer_markers=["Fishing-Funds-", ".AppImage"],
   href_exclude_substrings=_ex("arm64", "windows", "dmg", "Setup"),
   installer_extensions=[".AppImage"],
   aliases=["fishing funds", "Fishing Funds"])

# --- ClashX Meta ---
_e("darwin", SH_PROXY, "clashx_meta",
   "ClashX Meta（macOS Clash 菜单栏客户端；zip）", "代理与隧道",
   "MetaCubeX/ClashX.Meta",
   installer_markers_match_all=True,
   installer_markers=["ClashX.Meta.zip"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".zip"],
   aliases=["clashx meta", "ClashX Meta", "ClashX.Meta"])


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
