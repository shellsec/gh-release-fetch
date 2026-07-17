#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Wave2：次薄分片 / 建议扩充主题（浏览器、终端、科学计算、工具等）。"""
from __future__ import annotations

import json
import os
import re
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
            "source",
            "src.",
            "-src",
            "symbols",
            "debug",
            "pdb",
            "sha256",
            ".sig",
            ".asc",
            ".json",
            ".txt",
            ".md",
            "checksum",
            ".pem",
            ".sbom",
            ".blockmap",
            ".mar",
            "-ndm",
            ".yml",
        ],
    }
    d.update(kw)
    return d


def _repo(repo: str) -> dict:
    return {
        "releases_url": f"https://bgithub.xyz/{repo}/releases",
        "repo_path": repo,
    }


def _slug(repo: str) -> str:
    name = repo.split("/")[-1]
    s = re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_").lower()
    return s or "app"


def _desk(
    repo: str,
    shard: str,
    分类: str,
    简介: str,
    *,
    id: str | None = None,
    plats=("windows", "linux", "darwin"),
    **cfg,
):
    aid = id or _slug(repo)
    for p in plats:
        _add(p, shard, [{"id": aid, "简介": 简介, "分类": 分类, **_b(**cfg), **_repo(repo)}])


def _open_page(repo: str, shard: str, 分类: str, 简介: str, *, id: str | None = None, plats=("windows", "linux", "darwin")):
    aid = id or _slug(repo)
    for p in plats:
        _add(
            p,
            shard,
            [
                {
                    "id": aid,
                    "简介": 简介,
                    "分类": 分类,
                    "enabled": False,
                    "open_page_only": True,
                    "open_page_url": f"https://github.com/{repo}/releases",
                    **_repo(repo),
                }
            ],
        )


# --- 18 网络：浏览器 ---
_desk(
    "ungoogled-software/ungoogled-chromium-windows",
    "18-网络.json",
    "网络",
    "ungoogled-chromium（去 Google 集成的 Chromium；Windows x64 安装包）",
    id="ungoogled_chromium",
    plats=("windows",),
    installer_markers_match_all=True,
    installer_markers=["ungoogled-chromium_", "installer_x64.exe"],
    href_exclude_substrings=["arm64", "x86", ".zip", ".mar"],
    installer_extensions=[".exe"],
    windows_installer=True,
    run_installer=True,
)
_open_page(
    "ungoogled-software/ungoogled-chromium-windows",
    "18-网络.json",
    "网络",
    "ungoogled-chromium（Windows 专用构建；其他平台请打开 Releases 页）",
    id="ungoogled_chromium",
    plats=("linux", "darwin"),
)
_desk(
    "floorp-Projects/Floorp",
    "18-网络.json",
    "网络",
    "Floorp（Firefox 系注重隐私/自定义的浏览器）",
    id="floorp",
    plats=("windows",),
    installer_markers=["floorp-windows-x86_64.installer.exe"],
    href_exclude_substrings=["stub", ".mar", "meta.json", "linux", "mac", "noraneko"],
    installer_extensions=[".exe"],
    windows_installer=True,
    run_installer=True,
)
_desk(
    "floorp-Projects/Floorp",
    "18-网络.json",
    "网络",
    "Floorp（Firefox 系浏览器；macOS universal DMG）",
    id="floorp",
    plats=("darwin",),
    installer_markers=["floorp-macOS-universal.dmg"],
    href_exclude_substrings=[".mar", "meta.json", "windows", "linux", "noraneko"],
    installer_extensions=[".dmg"],
)
_desk(
    "floorp-Projects/Floorp",
    "18-网络.json",
    "网络",
    "Floorp（Firefox 系浏览器；Linux x86_64）",
    id="floorp",
    plats=("linux",),
    installer_markers_match_all=True,
    installer_markers=["floorp-linux-x86_64.tar.xz"],
    href_exclude_substrings=[".mar", "meta.json", "aarch64", "windows", "mac", ".deb", "noraneko"],
    installer_extensions=[".tar.xz"],
)
_desk(
    "mullvad/mullvad-browser",
    "18-网络.json",
    "网络",
    "Mullvad Browser（隐私浏览器）",
    id="mullvad_browser",
    plats=("windows",),
    installer_markers_match_all=True,
    installer_markers=["mullvad-browser-windows-x86_64-", ".exe"],
    href_exclude_substrings=[".asc", ".deb", "linux", "macos"],
    installer_extensions=[".exe"],
    windows_installer=True,
    run_installer=True,
)
_desk(
    "mullvad/mullvad-browser",
    "18-网络.json",
    "网络",
    "Mullvad Browser（隐私浏览器；Linux deb）",
    id="mullvad_browser",
    plats=("linux",),
    installer_markers_match_all=True,
    installer_markers=["mullvad-browser_", "amd64.deb"],
    href_exclude_substrings=[".asc", "windows", "macos"],
    installer_extensions=[".deb"],
)
_open_page(
    "mullvad/mullvad-browser",
    "18-网络.json",
    "网络",
    "Mullvad Browser（macOS 请打开 Releases 页）",
    id="mullvad_browser",
    plats=("darwin",),
)

# --- 17 终端 ---
_desk(
    "contour-terminal/contour",
    "17-终端.json",
    "终端",
    "Contour（现代 GPU 加速终端）",
    id="contour",
    plats=("windows",),
    installer_markers=["contour-", "win64.msi"],
    href_exclude_substrings=[".zip", "ubuntu", "dbgsym", ".ddeb", ".deb"],
    installer_extensions=[".msi"],
    windows_installer=True,
    run_installer=True,
)
_desk(
    "contour-terminal/contour",
    "17-终端.json",
    "终端",
    "Contour（现代 GPU 加速终端；Ubuntu deb）",
    id="contour",
    plats=("linux",),
    installer_markers_match_all=True,
    installer_markers=["contour-", "ubuntu24.04-amd64.deb"],
    href_exclude_substrings=["dbgsym", "win", ".msi", ".zip"],
    installer_extensions=[".deb"],
)
_open_page(
    "contour-terminal/contour",
    "17-终端.json",
    "终端",
    "Contour（macOS 请打开 Releases 页）",
    id="contour",
    plats=("darwin",),
)

# --- 06 命令行 ---
_desk(
    "gokcehan/lf",
    "06-命令行.json",
    "命令行",
    "lf（终端文件管理器）",
    id="lf",
    plats=("windows",),
    installer_markers=["lf-windows-amd64.zip"],
    href_exclude_substrings=["386", "darwin", "linux", "freebsd"],
    installer_extensions=[".zip"],
)
_desk(
    "gokcehan/lf",
    "06-命令行.json",
    "命令行",
    "lf（终端文件管理器；macOS Apple Silicon）",
    id="lf",
    plats=("darwin",),
    installer_markers=["lf-darwin-arm64.tar.gz"],
    href_exclude_substrings=["amd64", "windows", "linux"],
    installer_extensions=[".tar.gz"],
)
_desk(
    "gokcehan/lf",
    "06-命令行.json",
    "命令行",
    "lf（终端文件管理器；Linux amd64）",
    id="lf",
    plats=("linux",),
    installer_markers=["lf-linux-amd64.tar.gz"],
    href_exclude_substrings=["arm", "windows", "darwin", "freebsd"],
    installer_extensions=[".tar.gz"],
)

# --- 11 工具 ---
_desk(
    "mcmilk/7-Zip-zstd",
    "11-工具.json",
    "工具",
    "7-Zip ZS（带 Zstd 等额外算法的 7-Zip）",
    id="7zip_zstd",
    plats=("windows",),
    installer_markers=["7z26.02-zstd-x64.exe"],
    href_exclude_substrings=["arm64", "x86", "-ndm"],
    installer_extensions=[".exe"],
    windows_installer=True,
    run_installer=True,
)
_open_page(
    "mcmilk/7-Zip-zstd",
    "11-工具.json",
    "工具",
    "7-Zip ZS（仅 Windows；其他平台请打开 Releases 页）",
    id="7zip_zstd",
    plats=("linux", "darwin"),
)
_desk(
    "LibreHardwareMonitor/LibreHardwareMonitor",
    "16-系统.json",
    "系统",
    "LibreHardwareMonitor（硬件温度/风扇/负载监控）",
    id="libre_hardware_monitor",
    plats=("windows",),
    installer_markers=["LibreHardwareMonitor.zip"],
    href_exclude_substrings=[".NET.10", "source"],
    installer_extensions=[".zip"],
)
_open_page(
    "LibreHardwareMonitor/LibreHardwareMonitor",
    "16-系统.json",
    "系统",
    "LibreHardwareMonitor（仅 Windows；其他平台请打开 Releases 页）",
    id="libre_hardware_monitor",
    plats=("linux", "darwin"),
)

# --- 12 开发：科学计算 ---
_desk(
    "jupyterlab/jupyterlab-desktop",
    "12-开发.json",
    "开发",
    "JupyterLab Desktop（官方桌面版 JupyterLab）",
    id="jupyterlab_desktop",
    plats=("windows",),
    installer_markers=["JupyterLab-Setup-Windows-x64.exe"],
    href_exclude_substrings=["macOS", "Debian", "Fedora", ".dmg", ".deb", ".rpm", ".zip"],
    installer_extensions=[".exe"],
    windows_installer=True,
    run_installer=True,
)
_desk(
    "jupyterlab/jupyterlab-desktop",
    "12-开发.json",
    "开发",
    "JupyterLab Desktop（macOS x64 DMG）",
    id="jupyterlab_desktop",
    plats=("darwin",),
    installer_markers=["JupyterLab-Setup-macOS-x64.dmg"],
    href_exclude_substrings=["Windows", "Debian", "Fedora", ".zip", ".deb"],
    installer_extensions=[".dmg"],
)
_desk(
    "jupyterlab/jupyterlab-desktop",
    "12-开发.json",
    "开发",
    "JupyterLab Desktop（Linux Debian x64）",
    id="jupyterlab_desktop",
    plats=("linux",),
    installer_markers=["JupyterLab-Setup-Debian-x64.deb"],
    href_exclude_substrings=["Windows", "macOS", "Fedora", ".rpm", ".exe", ".dmg"],
    installer_extensions=[".deb"],
)
_desk(
    "spyder-ide/spyder",
    "12-开发.json",
    "开发",
    "Spyder（Python 科学计算 IDE）",
    id="spyder",
    plats=("windows",),
    installer_markers=["Spyder-Windows-x86_64.exe"],
    href_exclude_substrings=["macOS", "Linux", ".dmg", ".pkg"],
    installer_extensions=[".exe"],
    windows_installer=True,
    run_installer=True,
)
_open_page(
    "spyder-ide/spyder",
    "12-开发.json",
    "开发",
    "Spyder（非 Windows 安装包请打开 Releases/conda 页）",
    id="spyder",
    plats=("linux", "darwin"),
)
_desk(
    "wxMaxima-developers/wxmaxima",
    "12-开发.json",
    "开发",
    "wxMaxima（Maxima 计算机代数 GUI）",
    id="wxmaxima",
    plats=("windows",),
    installer_markers=["wxMaxima-", "win64.exe"],
    href_exclude_substrings=[".tar.", "source", "mac", "linux"],
    installer_extensions=[".exe"],
    windows_installer=True,
    run_installer=True,
)
_open_page(
    "wxMaxima-developers/wxmaxima",
    "12-开发.json",
    "开发",
    "wxMaxima（非 Windows 请打开 Releases/发行版包）",
    id="wxmaxima",
    plats=("linux", "darwin"),
)
_desk(
    "FiloSottile/mkcert",
    "12-开发.json",
    "开发",
    "mkcert（本地 HTTPS 开发证书）",
    id="mkcert",
    plats=("windows",),
    installer_markers=["mkcert-", "windows-amd64.exe"],
    href_exclude_substrings=["arm64", "linux", "darwin"],
    installer_extensions=[".exe"],
)
_desk(
    "FiloSottile/mkcert",
    "12-开发.json",
    "开发",
    "mkcert（本地 HTTPS 开发证书；macOS Apple Silicon）",
    id="mkcert",
    plats=("darwin",),
    installer_markers=["mkcert-", "darwin-arm64"],
    href_exclude_substrings=["amd64", "linux", "windows"],
)
_desk(
    "FiloSottile/mkcert",
    "12-开发.json",
    "开发",
    "mkcert（本地 HTTPS 开发证书；Linux amd64）",
    id="mkcert",
    plats=("linux",),
    installer_markers=["mkcert-", "linux-amd64"],
    href_exclude_substrings=["arm", "darwin", "windows"],
)

# --- 24 云原生：虚拟机 ---
_desk(
    "canonical/multipass",
    "24-云原生.json",
    "云原生",
    "Multipass（Canonical 轻量 Ubuntu VM）",
    id="multipass",
    plats=("windows",),
    installer_markers_match_all=True,
    installer_markers=["multipass-", "win-win64.msi"],
    href_exclude_substrings=["mac", "Darwin", ".pkg"],
    installer_extensions=[".msi"],
    windows_installer=True,
    run_installer=True,
)
_desk(
    "canonical/multipass",
    "24-云原生.json",
    "云原生",
    "Multipass（Canonical 轻量 Ubuntu VM；macOS）",
    id="multipass",
    plats=("darwin",),
    installer_markers_match_all=True,
    installer_markers=["multipass-", "mac-Darwin.pkg"],
    href_exclude_substrings=["win", ".msi"],
    installer_extensions=[".pkg"],
)
_open_page(
    "canonical/multipass",
    "24-云原生.json",
    "云原生",
    "Multipass（Linux 请用 snap/发行版或打开 Releases 页）",
    id="multipass",
    plats=("linux",),
)

# --- 15 笔记 / 教育 ---
_desk(
    "ankitects/anki",
    "15-笔记.json",
    "笔记",
    "Anki（间隔重复记忆卡片）",
    id="anki",
    plats=("windows",),
    installer_markers=["anki-", "win-x64.msi"],
    href_exclude_substrings=["arm64", "mac", "linux", ".dmg", ".tar."],
    installer_extensions=[".msi"],
    windows_installer=True,
    run_installer=True,
)
_desk(
    "ankitects/anki",
    "15-笔记.json",
    "笔记",
    "Anki（间隔重复记忆卡片；macOS Apple Silicon）",
    id="anki",
    plats=("darwin",),
    installer_markers=["anki-", "mac-apple.dmg"],
    href_exclude_substrings=["intel", "win", "linux"],
    installer_extensions=[".dmg"],
)
_desk(
    "ankitects/anki",
    "15-笔记.json",
    "笔记",
    "Anki（间隔重复记忆卡片；Linux x86_64）",
    id="anki",
    plats=("linux",),
    installer_markers=["anki-", "linux-x86_64.tar.zst"],
    href_exclude_substrings=["aarch64", "win", "mac"],
    installer_extensions=[".tar.zst"],
)

# --- 02 下载 ---
_desk(
    "nicotine-plus/nicotine-plus",
    "02-下载.json",
    "下载",
    "Nicotine+（Soulseek 图形客户端）",
    id="nicotine_plus",
    plats=("windows",),
    installer_markers=["windows-x86_64-installer.zip"],
    href_exclude_substrings=["package", ".sha256", "linux", "macos"],
    installer_extensions=[".zip"],
)
_open_page(
    "nicotine-plus/nicotine-plus",
    "02-下载.json",
    "下载",
    "Nicotine+（非 Windows 请用发行版包或打开 Releases 页）",
    id="nicotine_plus",
    plats=("linux", "darwin"),
)


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


def _merge_desktop(dry: bool) -> tuple[int, int]:
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
            rp = (app.get("repo_path") or "").lower()
            aid = (app.get("id") or "").strip()
            if rp in seen_repos or aid in seen_ids or aid in file_ids:
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
    a1, s1 = _merge_desktop(dry)
    print(f"{'dry-run' if dry else 'done'}: desktop +{a1} skip {s1}")


if __name__ == "__main__":
    main()
