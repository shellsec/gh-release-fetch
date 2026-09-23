#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Batch24：开源电影/剧集/音乐/游戏库（有 GitHub Release 安装包）。"""
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


SH_AV = "22-音视频.json"
SH_GAME = "14-游戏.json"

EX_JUNK = [
    "source", "src.", "-src", "symbols", "debug", "pdb",
    "sha256", ".sig", ".asc", ".json", ".txt", ".md",
    "checksum", ".yml", ".blockmap", ".minisig", ".apk",
]


def _ex(*extra):
    return EX_JUNK + list(extra)


# --- Radarr：电影媒体库 ---
_e("windows", SH_AV, "radarr",
   "Radarr（电影媒体库管理；Windows x64 安装包）", "音视频",
   "Radarr/Radarr",
   installer_markers_match_all=True,
   installer_markers=["Radarr.master.", "windows-core-x64-installer.exe"],
   href_exclude_substrings=_ex("x86", "linux", "osx", "freebsd", ".zip"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["radarr", "Radarr", "电影库", "电影刮削"])
_e("darwin", SH_AV, "radarr",
   "Radarr（电影媒体库管理；macOS Apple Silicon app zip）", "音视频",
   "Radarr/Radarr",
   installer_markers_match_all=True,
   installer_markers=["Radarr.master.", "osx-app-core-arm64.zip"],
   href_exclude_substrings=_ex("osx-core", "x64", "linux", "windows", "freebsd"),
   installer_extensions=[".zip"],
   aliases=["radarr", "Radarr", "电影库", "电影刮削"])
_e("linux", SH_AV, "radarr",
   "Radarr（电影媒体库管理；Linux x64 tar.gz）", "音视频",
   "Radarr/Radarr",
   installer_markers_match_all=True,
   installer_markers=["Radarr.master.", "linux-core-x64.tar.gz"],
   href_exclude_substrings=_ex("musl", "arm", "osx", "windows", "freebsd"),
   installer_extensions=[".tar.gz"],
   aliases=["radarr", "Radarr", "电影库", "电影刮削"])

# --- Sonarr：剧集媒体库 ---
_e("windows", SH_AV, "sonarr",
   "Sonarr（剧集媒体库管理；Windows x64 安装包）", "音视频",
   "Sonarr/Sonarr",
   installer_markers_match_all=True,
   installer_markers=["Sonarr.main.", "win-x64-installer.exe"],
   href_exclude_substrings=_ex("x86", "linux", "osx", "freebsd", ".zip"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["sonarr", "Sonarr", "剧集库", "电视剧"])
_e("darwin", SH_AV, "sonarr",
   "Sonarr（剧集媒体库管理；macOS Apple Silicon app zip）", "音视频",
   "Sonarr/Sonarr",
   installer_markers_match_all=True,
   installer_markers=["Sonarr.main.", "osx-arm64-app.zip"],
   href_exclude_substrings=_ex("osx-x64", "osx-arm64.tar", "linux", "win-", "freebsd"),
   installer_extensions=[".zip"],
   aliases=["sonarr", "Sonarr", "剧集库", "电视剧"])
_e("linux", SH_AV, "sonarr",
   "Sonarr（剧集媒体库管理；Linux x64 tar.gz）", "音视频",
   "Sonarr/Sonarr",
   installer_markers_match_all=True,
   installer_markers=["Sonarr.main.", "linux-x64.tar.gz"],
   href_exclude_substrings=_ex("musl", "arm", "osx", "win-", "freebsd"),
   installer_extensions=[".tar.gz"],
   aliases=["sonarr", "Sonarr", "剧集库", "电视剧"])

# --- Prowlarr：索引器管理 ---
_e("windows", SH_AV, "prowlarr",
   "Prowlarr（媒体库索引器管理，配合 Radarr/Sonarr/Lidarr；Windows x64 安装包）", "音视频",
   "Prowlarr/Prowlarr",
   installer_markers_match_all=True,
   installer_markers=["Prowlarr.master.", "windows-core-x64-installer.exe"],
   href_exclude_substrings=_ex("x86", "linux", "osx", "freebsd", ".zip"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["prowlarr", "Prowlarr", "索引器"])
_e("darwin", SH_AV, "prowlarr",
   "Prowlarr（媒体库索引器管理；macOS Apple Silicon app zip）", "音视频",
   "Prowlarr/Prowlarr",
   installer_markers_match_all=True,
   installer_markers=["Prowlarr.master.", "osx-app-core-arm64.zip"],
   href_exclude_substrings=_ex("osx-core", "x64", "linux", "windows", "freebsd"),
   installer_extensions=[".zip"],
   aliases=["prowlarr", "Prowlarr", "索引器"])
_e("linux", SH_AV, "prowlarr",
   "Prowlarr（媒体库索引器管理；Linux x64 tar.gz）", "音视频",
   "Prowlarr/Prowlarr",
   installer_markers_match_all=True,
   installer_markers=["Prowlarr.master.", "linux-core-x64.tar.gz"],
   href_exclude_substrings=_ex("musl", "arm", "osx", "windows", "freebsd"),
   installer_extensions=[".tar.gz"],
   aliases=["prowlarr", "Prowlarr", "索引器"])

# --- Lidarr：音乐媒体库 ---
_e("windows", SH_AV, "lidarr",
   "Lidarr（音乐媒体库管理；Windows x64 安装包）", "音视频",
   "Lidarr/Lidarr",
   installer_markers_match_all=True,
   installer_markers=["Lidarr.master.", "windows-core-x64-installer.exe"],
   href_exclude_substrings=_ex("x86", "linux", "osx", "freebsd", ".zip"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["lidarr", "Lidarr", "音乐库"])
_e("darwin", SH_AV, "lidarr",
   "Lidarr（音乐媒体库管理；macOS Apple Silicon app zip）", "音视频",
   "Lidarr/Lidarr",
   installer_markers_match_all=True,
   installer_markers=["Lidarr.master.", "osx-app-core-arm64.zip"],
   href_exclude_substrings=_ex("osx-core", "x64", "linux", "windows", "freebsd"),
   installer_extensions=[".zip"],
   aliases=["lidarr", "Lidarr", "音乐库"])
_e("linux", SH_AV, "lidarr",
   "Lidarr（音乐媒体库管理；Linux x64 tar.gz）", "音视频",
   "Lidarr/Lidarr",
   installer_markers_match_all=True,
   installer_markers=["Lidarr.master.", "linux-core-x64.tar.gz"],
   href_exclude_substrings=_ex("musl", "arm", "osx", "windows", "freebsd"),
   installer_extensions=[".tar.gz"],
   aliases=["lidarr", "Lidarr", "音乐库"])

# --- Bazarr：字幕管理 ---
_e("windows", SH_AV, "bazarr",
   "Bazarr（媒体库字幕管理，配合 Sonarr/Radarr；官方 zip）", "音视频",
   "morpheus65535/bazarr",
   installer_markers_match_all=True,
   installer_markers=["bazarr.zip"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".zip"],
   aliases=["bazarr", "Bazarr", "字幕管理"])
_e("darwin", SH_AV, "bazarr",
   "Bazarr（媒体库字幕管理，配合 Sonarr/Radarr；官方 zip）", "音视频",
   "morpheus65535/bazarr",
   installer_markers_match_all=True,
   installer_markers=["bazarr.zip"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".zip"],
   aliases=["bazarr", "Bazarr", "字幕管理"])
_e("linux", SH_AV, "bazarr",
   "Bazarr（媒体库字幕管理，配合 Sonarr/Radarr；官方 zip）", "音视频",
   "morpheus65535/bazarr",
   installer_markers_match_all=True,
   installer_markers=["bazarr.zip"],
   href_exclude_substrings=_ex(),
   installer_extensions=[".zip"],
   aliases=["bazarr", "Bazarr", "字幕管理"])

# --- Tautulli：Plex 库统计 ---
_e("windows", SH_AV, "tautulli",
   "Tautulli（Plex 媒体库统计与监控；Windows x64 安装包）", "音视频",
   "Tautulli/Tautulli",
   installer_markers_match_all=True,
   installer_markers=["Tautulli-windows-", "x64.exe"],
   href_exclude_substrings=_ex("macos", "linux"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["tautulli", "Tautulli", "Plex统计"])
_e("darwin", SH_AV, "tautulli",
   "Tautulli（Plex 媒体库统计与监控；macOS Apple Silicon pkg）", "音视频",
   "Tautulli/Tautulli",
   installer_markers_match_all=True,
   installer_markers=["Tautulli-macos-", "arm64.pkg"],
   href_exclude_substrings=_ex("x86_64", "windows", "linux"),
   installer_extensions=[".pkg"],
   aliases=["tautulli", "Tautulli", "Plex统计"])

# --- MediaElch：Kodi 刮削 ---
_e("windows", SH_AV, "mediaelch",
   "MediaElch（Kodi 媒体库刮削/NFO；Windows x64 zip）", "音视频",
   "Komet/MediaElch",
   installer_markers_match_all=True,
   installer_markers=["MediaElch_win_10_or_later_Qt6_", ".zip"],
   href_exclude_substrings=_ex("win_7", "linux", "macOS", "AppImage"),
   installer_extensions=[".zip"],
   aliases=["mediaelch", "MediaElch", "刮削", "Kodi刮削"])
_e("linux", SH_AV, "mediaelch",
   "MediaElch（Kodi 媒体库刮削/NFO；Linux x86_64 AppImage）", "音视频",
   "Komet/MediaElch",
   installer_markers_match_all=True,
   installer_markers=["MediaElch_linux_", ".AppImage"],
   href_exclude_substrings=_ex("win_", "macOS", ".zip"),
   installer_extensions=[".AppImage"],
   aliases=["mediaelch", "MediaElch", "刮削", "Kodi刮削"])

# --- IINA：macOS 播放器 ---
_e("darwin", SH_AV, "iina",
   "IINA（macOS 开源播放器，universal dmg，含 Apple Silicon）", "音视频",
   "iina/iina",
   installer_markers_match_all=True,
   installer_markers=["IINA.v", ".dmg"],
   href_exclude_substrings=_ex("beta", "nightly"),
   installer_extensions=[".dmg"],
   aliases=["iina", "IINA", "播放器"])

# --- Navidrome：音乐库服务器 ---
_e("windows", SH_AV, "navidrome",
   "Navidrome（自建音乐库服务器；Windows amd64 msi）", "音视频",
   "navidrome/navidrome",
   installer_markers_match_all=True,
   installer_markers=["navidrome_", "windows_amd64_installer.msi"],
   href_exclude_substrings=_ex("386", "linux", "darwin", ".zip"),
   installer_extensions=[".msi"], windows_installer=True, run_installer=True,
   aliases=["navidrome", "Navidrome", "音乐服务器"])
_e("darwin", SH_AV, "navidrome",
   "Navidrome（自建音乐库服务器；macOS Apple Silicon tar.gz）", "音视频",
   "navidrome/navidrome",
   installer_markers_match_all=True,
   installer_markers=["navidrome_", "darwin_arm64.tar.gz"],
   href_exclude_substrings=_ex("amd64", "linux", "windows"),
   installer_extensions=[".tar.gz"],
   aliases=["navidrome", "Navidrome", "音乐服务器"])
_e("linux", SH_AV, "navidrome",
   "Navidrome（自建音乐库服务器；Linux amd64 deb）", "音视频",
   "navidrome/navidrome",
   installer_markers_match_all=True,
   installer_markers=["navidrome_", "linux_amd64.deb"],
   href_exclude_substrings=_ex("arm", "386", "riscv", "windows", "darwin", ".rpm", ".tar.gz"),
   installer_extensions=[".deb"],
   aliases=["navidrome", "Navidrome", "音乐服务器"])

# --- Feishin：Jellyfin/Navidrome 音乐桌面 ---
_e("windows", SH_AV, "feishin",
   "Feishin（Jellyfin/Navidrome/Subsonic 音乐桌面；Windows x64 安装包）", "音视频",
   "jeffvli/feishin",
   installer_markers_match_all=True,
   installer_markers=["Feishin-", "win-x64.exe"],
   href_exclude_substrings=_ex("arm64", ".zip", "linux", "mac-"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["feishin", "Feishin", "Jellyfin音乐"])
_e("darwin", SH_AV, "feishin",
   "Feishin（Jellyfin/Navidrome/Subsonic 音乐桌面；macOS Apple Silicon dmg）", "音视频",
   "jeffvli/feishin",
   installer_markers_match_all=True,
   installer_markers=["Feishin-", "mac-arm64.dmg"],
   href_exclude_substrings=_ex("x64", ".zip", "win-", "linux"),
   installer_extensions=[".dmg"],
   aliases=["feishin", "Feishin", "Jellyfin音乐"])
_e("linux", SH_AV, "feishin",
   "Feishin（Jellyfin/Navidrome/Subsonic 音乐桌面；Linux x86_64 AppImage）", "音视频",
   "jeffvli/feishin",
   installer_markers_match_all=True,
   installer_markers=["Feishin-linux-x86_64.AppImage"],
   href_exclude_substrings=_ex("arm64", ".deb", ".tar.xz", "win-", "mac-"),
   installer_extensions=[".AppImage"],
   aliases=["feishin", "Feishin", "Jellyfin音乐"])

# --- Picard：音乐标签刮削 ---
_e("windows", SH_AV, "picard",
   "MusicBrainz Picard（音乐标签刮削；Windows 安装包）", "音视频",
   "metabrainz/picard",
   installer_markers_match_all=True,
   installer_markers=["picard-setup-", ".exe"],
   href_exclude_substrings=_ex("MusicBrainz-Picard", "msix", "macOS", "unsigned"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["picard", "Picard", "MusicBrainz", "音乐标签"])

# --- LRCGET：歌词工具 ---
_e("windows", SH_AV, "lrcget",
   "LRCGET（本地曲库歌词下载/嵌入；Windows x64 安装包）", "音视频",
   "tranxuanthang/lrcget",
   installer_markers_match_all=True,
   installer_markers=["LRCGET_", "x64-setup.exe"],
   href_exclude_substrings=_ex(".msi", ".dmg", "AppImage", ".deb"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["lrcget", "LRCGET", "歌词"])
_e("darwin", SH_AV, "lrcget",
   "LRCGET（本地曲库歌词下载/嵌入；macOS Apple Silicon dmg）", "音视频",
   "tranxuanthang/lrcget",
   installer_markers_match_all=True,
   installer_markers=["LRCGET_", "aarch64.dmg"],
   href_exclude_substrings=_ex("x64", "app.tar.gz", "setup.exe", "AppImage"),
   installer_extensions=[".dmg"],
   aliases=["lrcget", "LRCGET", "歌词"])
_e("linux", SH_AV, "lrcget",
   "LRCGET（本地曲库歌词下载/嵌入；Linux amd64 AppImage）", "音视频",
   "tranxuanthang/lrcget",
   installer_markers_match_all=True,
   installer_markers=["LRCGET_", "amd64.AppImage"],
   href_exclude_substrings=_ex(".deb", ".rpm", ".dmg", "setup.exe"),
   installer_extensions=[".AppImage"],
   aliases=["lrcget", "LRCGET", "歌词"])

# --- Tauon：本地音乐播放/库 ---
_e("windows", SH_AV, "tauon",
   "Tauon（本地音乐库播放器；Windows 安装包）", "音视频",
   "Taiko2k/Tauon",
   installer_markers_match_all=True,
   installer_markers=["TauonMusicBox-windows-installer.exe"],
   href_exclude_substrings=_ex(".7z", ".dmg", "linux"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["tauon", "Tauon", "TauonMusicBox", "音乐播放器"])
_e("darwin", SH_AV, "tauon",
   "Tauon（本地音乐库播放器；macOS 签名 dmg）", "音视频",
   "Taiko2k/Tauon",
   installer_markers_match_all=True,
   installer_markers=["Tauon-signed.dmg"],
   href_exclude_substrings=_ex("windows", "linux", ".7z"),
   installer_extensions=[".dmg"],
   aliases=["tauon", "Tauon", "TauonMusicBox", "音乐播放器"])
_e("linux", SH_AV, "tauon",
   "Tauon（本地音乐库播放器；Linux 便携 7z）", "音视频",
   "Taiko2k/Tauon",
   installer_markers_match_all=True,
   installer_markers=["TauonMusicBox-linux.7z"],
   href_exclude_substrings=_ex("windows", ".dmg", "installer"),
   installer_extensions=[".7z"],
   aliases=["tauon", "Tauon", "TauonMusicBox", "音乐播放器"])

# --- itch：itch.io 游戏库 ---
_e("windows", SH_GAME, "itch",
   "itch（itch.io 官方游戏库客户端；Windows amd64 tar.gz）", "游戏",
   "itchio/itch",
   installer_markers_match_all=True,
   installer_markers=["itch-v", "windows-amd64.tar.gz"],
   href_exclude_substrings=_ex("darwin", "linux", "arm64"),
   installer_extensions=[".tar.gz"],
   aliases=["itch", "itch.io", "itchio"])
_e("darwin", SH_GAME, "itch",
   "itch（itch.io 官方游戏库客户端；macOS Apple Silicon tar.gz）", "游戏",
   "itchio/itch",
   installer_markers_match_all=True,
   installer_markers=["itch-v", "darwin-arm64.tar.gz"],
   href_exclude_substrings=_ex("amd64", "windows", "linux"),
   installer_extensions=[".tar.gz"],
   aliases=["itch", "itch.io", "itchio"])
_e("linux", SH_GAME, "itch",
   "itch（itch.io 官方游戏库客户端；Linux amd64 tar.gz）", "游戏",
   "itchio/itch",
   installer_markers_match_all=True,
   installer_markers=["itch-v", "linux-amd64.tar.gz"],
   href_exclude_substrings=_ex("darwin", "windows", "arm64"),
   installer_extensions=[".tar.gz"],
   aliases=["itch", "itch.io", "itchio"])

# --- Legendary：Epic CLI ---
_e("windows", SH_GAME, "legendary",
   "Legendary（Epic Games 开源命令行启动器；Windows x64 exe）", "游戏",
   "legendary-gl/legendary",
   installer_markers_match_all=True,
   installer_markers=["legendary_windows_x64.exe"],
   href_exclude_substrings=_ex("arm64", "linux", "macOS"),
   installer_extensions=[".exe"],
   aliases=["legendary", "Legendary", "Epic CLI"])
_e("darwin", SH_GAME, "legendary",
   "Legendary（Epic Games 开源命令行启动器；macOS Apple Silicon 二进制）", "游戏",
   "legendary-gl/legendary",
   installer_markers_match_all=True,
   installer_markers=["legendary_macOS_arm64"],
   href_exclude_substrings=_ex("x64", "windows", "linux", ".zip"),
   aliases=["legendary", "Legendary", "Epic CLI"])
_e("linux", SH_GAME, "legendary",
   "Legendary（Epic Games 开源命令行启动器；Linux x64 二进制）", "游戏",
   "legendary-gl/legendary",
   installer_markers_match_all=True,
   installer_markers=["legendary_linux_x64"],
   href_exclude_substrings=_ex("arm64", "windows", "macOS"),
   aliases=["legendary", "Legendary", "Epic CLI"])


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
