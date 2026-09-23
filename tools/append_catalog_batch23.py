#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Batch23：开源资源/素材/内容库类（有 GitHub Release 安装包）。"""
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


SH_WRITE = "03-写作.json"
SH_OFFICE = "04-办公.json"
SH_DESIGN = "05-办公与设计.json"
SH_MEDIA = "08-多媒体.json"
SH_TOOL = "11-工具.json"
SH_SHARE = "29-局域网文件共享.json"

# --- Kavita：电子书/漫画库 ---
_e("windows", SH_OFFICE, "kavita",
   "Kavita（开源电子书/漫画库服务器；Windows x64 tar.gz）", "办公",
   "Kareadita/Kavita",
   installer_markers_match_all=True,
   installer_markers=["kavita-win-x64.tar.gz"],
   href_exclude_substrings=["win-x86", "linux", "osx", "arm", "musl"],
   installer_extensions=[".tar.gz"],
   aliases=["kavita", "Kavita", "电子书库", "漫画库"])
_e("darwin", SH_OFFICE, "kavita",
   "Kavita（开源电子书/漫画库服务器；macOS Apple Silicon tar.gz）", "办公",
   "Kareadita/Kavita",
   installer_markers_match_all=True,
   installer_markers=["kavita-osx-arm64.tar.gz"],
   href_exclude_substrings=["osx-x64", "linux", "win-", "musl"],
   installer_extensions=[".tar.gz"],
   aliases=["kavita", "Kavita", "电子书库", "漫画库"])
_e("linux", SH_OFFICE, "kavita",
   "Kavita（开源电子书/漫画库服务器；Linux x64 tar.gz）", "办公",
   "Kareadita/Kavita",
   installer_markers_match_all=True,
   installer_markers=["kavita-linux-x64.tar.gz"],
   href_exclude_substrings=["musl", "arm", "osx", "win-"],
   installer_extensions=[".tar.gz"],
   aliases=["kavita", "Kavita", "电子书库", "漫画库"])

# --- OpenList：AList 社区续作 ---
_e("windows", SH_SHARE, "openlist",
   "OpenList（AList 开源续作，多网盘挂载；Windows amd64 zip）", "局域网文件共享",
   "OpenListTeam/OpenList",
   installer_markers_match_all=True,
   installer_markers=["openlist-windows-amd64.zip"],
   href_exclude_substrings=["lite", "windows7", "arm64", "386", "android", "linux", "darwin"],
   installer_extensions=[".zip"],
   aliases=["openlist", "OpenList", "AList续作", "网盘挂载"])
_e("darwin", SH_SHARE, "openlist",
   "OpenList（AList 开源续作；macOS Apple Silicon tar.gz）", "局域网文件共享",
   "OpenListTeam/OpenList",
   installer_markers_match_all=True,
   installer_markers=["openlist-darwin-arm64.tar.gz"],
   href_exclude_substrings=["lite", "amd64", "android", "linux", "windows"],
   installer_extensions=[".tar.gz"],
   aliases=["openlist", "OpenList", "AList续作", "网盘挂载"])
_e("linux", SH_SHARE, "openlist",
   "OpenList（AList 开源续作；Linux amd64 tar.gz）", "局域网文件共享",
   "OpenListTeam/OpenList",
   installer_markers_match_all=True,
   installer_markers=["openlist-linux-amd64.tar.gz"],
   href_exclude_substrings=["lite", "musl", "arm", "386", "android", "windows", "darwin"],
   installer_extensions=[".tar.gz"],
   aliases=["openlist", "OpenList", "AList续作", "网盘挂载"])

# --- TagSpaces：本地文件/素材标签库 ---
_e("windows", SH_TOOL, "tagspaces",
   "TagSpaces（本地文件标签与素材库；Windows x64 安装包）", "工具",
   "tagspaces/tagspaces",
   installer_markers_match_all=True,
   installer_markers=["tagspaces-win-x64-", ".exe"],
   href_exclude_substrings=["arm64", ".zip", ".blockmap", "linux", "mac-", ".apk"],
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["tagspaces", "TagSpaces", "文件标签", "素材库"])
_e("darwin", SH_TOOL, "tagspaces",
   "TagSpaces（本地文件标签与素材库；macOS Apple Silicon dmg）", "工具",
   "tagspaces/tagspaces",
   installer_markers_match_all=True,
   installer_markers=["tagspaces-mac-arm64-", ".dmg"],
   href_exclude_substrings=["x64", ".pkg", "win-", "linux", ".apk"],
   installer_extensions=[".dmg"],
   aliases=["tagspaces", "TagSpaces", "文件标签", "素材库"])
_e("linux", SH_TOOL, "tagspaces",
   "TagSpaces（本地文件标签与素材库；Linux x86_64 AppImage）", "工具",
   "tagspaces/tagspaces",
   installer_markers_match_all=True,
   installer_markers=["tagspaces-linux-x86_64-", ".AppImage"],
   href_exclude_substrings=["arm64", ".deb", ".tar.gz", "win-", "mac-", ".apk"],
   installer_extensions=[".AppImage"],
   aliases=["tagspaces", "TagSpaces", "文件标签", "素材库"])

# --- Hydrus Network：媒体资源整理 ---
_e("windows", SH_MEDIA, "hydrus",
   "Hydrus Network（本地媒体/图库标签整理；Windows 安装包）", "多媒体",
   "hydrusnetwork/hydrus",
   installer_markers_match_all=True,
   installer_markers=["Windows", "Installer.exe"],
   href_exclude_substrings=["Extract", "Linux", ".zip", ".tar", "pdb"],
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["hydrus", "Hydrus", "Hydrus Network", "图库整理"])
_e("linux", SH_MEDIA, "hydrus",
   "Hydrus Network（本地媒体/图库标签整理；Linux Executable tar.zst）", "多媒体",
   "hydrusnetwork/hydrus",
   installer_markers_match_all=True,
   installer_markers=["Linux", "Executable.tar.zst"],
   href_exclude_substrings=["Windows", ".zip", "Installer"],
   installer_extensions=[".zst", ".tar.zst"],
   aliases=["hydrus", "Hydrus", "Hydrus Network", "图库整理"])

# --- FontForge：字体编辑 ---
_e("windows", SH_DESIGN, "fontforge",
   "FontForge（开源字体编辑器；Windows x64 安装包）", "办公与设计",
   "fontforge/fontforge",
   installer_markers_match_all=True,
   installer_markers=["FontForge-", "Windows-x64.exe"],
   href_exclude_substrings=["Linux", "MacOS", ".tar.xz", "AppImage"],
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["fontforge", "FontForge", "字体编辑", "字体"])
_e("darwin", SH_DESIGN, "fontforge",
   "FontForge（开源字体编辑器；macOS dmg）", "办公与设计",
   "fontforge/fontforge",
   installer_markers_match_all=True,
   installer_markers=["FontForge-", "MacOS.app.dmg"],
   href_exclude_substrings=["Linux", "Windows", ".tar.xz", "AppImage"],
   installer_extensions=[".dmg"],
   aliases=["fontforge", "FontForge", "字体编辑", "字体"])
_e("linux", SH_DESIGN, "fontforge",
   "FontForge（开源字体编辑器；Linux x86_64 AppImage）", "办公与设计",
   "fontforge/fontforge",
   installer_markers_match_all=True,
   installer_markers=["FontForge-", "Linux-x86_64.AppImage"],
   href_exclude_substrings=["Windows", "MacOS", ".tar.xz"],
   installer_extensions=[".AppImage"],
   aliases=["fontforge", "FontForge", "字体编辑", "字体"])

# --- Readest：现代电子书阅读 ---
_e("windows", SH_WRITE, "readest",
   "Readest（开源跨平台电子书阅读器；Windows x64 安装包）", "写作",
   "readest/readest",
   installer_markers_match_all=True,
   installer_markers=["Readest_", "x64-setup.exe"],
   href_exclude_substrings=["portable", "arm64", ".sig", "AppImage", ".dmg", ".apk"],
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["readest", "Readest", "电子书阅读"])
_e("darwin", SH_WRITE, "readest",
   "Readest（开源跨平台电子书阅读器；macOS universal dmg）", "写作",
   "readest/readest",
   installer_markers_match_all=True,
   installer_markers=["Readest_", "universal.dmg"],
   href_exclude_substrings=[".sig", "app.tar.gz", "setup.exe", "AppImage", ".apk"],
   installer_extensions=[".dmg"],
   aliases=["readest", "Readest", "电子书阅读"])
_e("linux", SH_WRITE, "readest",
   "Readest（开源跨平台电子书阅读器；Linux amd64 AppImage）", "写作",
   "readest/readest",
   installer_markers_match_all=True,
   installer_markers=["Readest_", "amd64.AppImage"],
   href_exclude_substrings=[".sig", "aarch64", ".deb", ".rpm", "setup.exe", ".apk"],
   installer_extensions=[".AppImage"],
   aliases=["readest", "Readest", "电子书阅读"])

# --- GoldenDict-ng：词典（写作配套） ---
_e("windows", SH_WRITE, "goldendict_ng",
   "GoldenDict-ng（开源词典/词库阅读器；Windows 安装包，Qt 6.10）", "写作",
   "xiaoyifang/goldendict-ng",
   installer_markers_match_all=True,
   installer_markers=["GoldenDict-ng-", "Qt6.10.3-Windows-installer.exe"],
   href_exclude_substrings=["exe-only", "Qt6.8", ".7z", ".pdb", "macOS"],
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["goldendict", "goldendict-ng", "GoldenDict", "词典", "字典"])
_e("darwin", SH_WRITE, "goldendict_ng",
   "GoldenDict-ng（开源词典/词库阅读器；macOS Apple Silicon dmg，Qt 6.10）", "写作",
   "xiaoyifang/goldendict-ng",
   installer_markers_match_all=True,
   installer_markers=["GoldenDict-ng-", "Qt6.10.3-macOS-arm64.dmg"],
   href_exclude_substrings=["x86_64", "Qt6.8", "Windows"],
   installer_extensions=[".dmg"],
   aliases=["goldendict", "goldendict-ng", "GoldenDict", "词典", "字典"])

# --- Foliate：Linux EPUB 阅读 ---
_e("linux", SH_WRITE, "foliate",
   "Foliate（GNOME 电子书阅读器；Linux all.deb）", "写作",
   "johnfactotum/foliate",
   installer_markers_match_all=True,
   installer_markers=["foliate_", "_all.deb"],
   href_exclude_substrings=["tar.xz", "sha256"],
   installer_extensions=[".deb"],
   aliases=["foliate", "Foliate", "电子书阅读"])


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
