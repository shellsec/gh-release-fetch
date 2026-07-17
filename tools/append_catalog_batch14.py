#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Wave1：薄分类主动补齐（写作/办公/备份/协作/通讯/远程/音视频/可观测/金融/代理）。"""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS = os.path.join(ROOT, "apps")

BATCH: dict[tuple[str, list]] = {}


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
            ".dgst",
            ".zsync",
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


def _win(repo, shard, 分类, 简介, **cfg):
    _desk(repo, shard, 分类, 简介, plats=("windows",), **cfg)


def _open_page(repo: str, shard: str, 分类: str, 简介: str, *, id: str | None = None, plats=("windows", "linux", "darwin")):
    aid = id or _slug(repo)
    for p in plats:
        note = {
            "windows": "Windows",
            "darwin": "macOS",
            "linux": "Linux",
        }.get(p, p)
        _add(
            p,
            shard,
            [
                {
                    "id": aid,
                    "简介": f"{简介}（请打开 Releases 页）" if "请打开" not in 简介 else 简介,
                    "分类": 分类,
                    "enabled": False,
                    "open_page_only": True,
                    "open_page_url": f"https://github.com/{repo}/releases",
                    **_repo(repo),
                }
            ],
        )


# --- 05 办公与设计 ---
_desk(
    "LibreCAD/LibreCAD",
    "05-办公与设计.json",
    "办公与设计",
    "LibreCAD（开源 2D CAD）",
    id="librecad",
    plats=("windows",),
    installer_markers_match_all=True,
    installer_markers=["LibreCAD-", "win64-msvc.exe"],
    href_exclude_substrings=["AppImage", ".dmg", ".snap", "arm64", "LICENSE"],
    installer_extensions=[".exe"],
    windows_installer=True,
    run_installer=True,
)
_desk(
    "LibreCAD/LibreCAD",
    "05-办公与设计.json",
    "办公与设计",
    "LibreCAD（开源 2D CAD；macOS DMG）",
    id="librecad",
    plats=("darwin",),
    installer_markers_match_all=True,
    installer_markers=["LibreCAD-", ".dmg"],
    href_exclude_substrings=["AppImage", ".exe", ".snap", "arm64"],
    installer_extensions=[".dmg"],
)
_desk(
    "LibreCAD/LibreCAD",
    "05-办公与设计.json",
    "办公与设计",
    "LibreCAD（开源 2D CAD；Linux x86_64 AppImage）",
    id="librecad",
    plats=("linux",),
    installer_markers_match_all=True,
    installer_markers=["LibreCAD-", "x86_64.AppImage"],
    href_exclude_substrings=[".exe", ".dmg", ".snap", "aarch64"],
    installer_extensions=[".AppImage"],
)
_desk(
    "pencil2d/pencil",
    "05-办公与设计.json",
    "办公与设计",
    "Pencil2D（开源 2D 手绘动画）",
    id="pencil2d",
    plats=("windows",),
    installer_markers_match_all=True,
    installer_markers=["pencil2d-win64-", ".zip"],
    href_exclude_substrings=["win32", "AppImage", ".dmg"],
    installer_extensions=[".zip"],
)
_desk(
    "pencil2d/pencil",
    "05-办公与设计.json",
    "办公与设计",
    "Pencil2D（开源 2D 手绘动画；macOS DMG）",
    id="pencil2d",
    plats=("darwin",),
    installer_markers_match_all=True,
    installer_markers=["pencil2d-mac-", ".dmg"],
    href_exclude_substrings=["win", "AppImage"],
    installer_extensions=[".dmg"],
)
_desk(
    "pencil2d/pencil",
    "05-办公与设计.json",
    "办公与设计",
    "Pencil2D（开源 2D 手绘动画；Linux AppImage）",
    id="pencil2d",
    plats=("linux",),
    installer_markers_match_all=True,
    installer_markers=["pencil2d-linux-amd64-", ".AppImage"],
    href_exclude_substrings=["i686", "win", ".dmg", ".zsync"],
    installer_extensions=[".AppImage"],
)

# --- 03 写作 ---
_desk(
    "quarto-dev/quarto-cli",
    "03-写作.json",
    "写作",
    "Quarto CLI（科学/技术写作发布：PDF/HTML/Word）",
    id="quarto_cli",
    plats=("windows",),
    installer_markers_match_all=True,
    installer_markers=["quarto-", "-win.msi"],
    href_exclude_substrings=[".zip", "checksum", "changelog", "linux", "macos", ".tar.gz"],
    installer_extensions=[".msi"],
    windows_installer=True,
    run_installer=True,
)
_desk(
    "quarto-dev/quarto-cli",
    "03-写作.json",
    "写作",
    "Quarto CLI（科学/技术写作发布；macOS pkg）",
    id="quarto_cli",
    plats=("darwin",),
    installer_markers_match_all=True,
    installer_markers=["quarto-", "-macos.pkg"],
    href_exclude_substrings=[".tar.gz", "win", "linux", "checksum"],
    installer_extensions=[".pkg"],
)
_desk(
    "quarto-dev/quarto-cli",
    "03-写作.json",
    "写作",
    "Quarto CLI（科学/技术写作发布；Linux amd64 tar.gz）",
    id="quarto_cli",
    plats=("linux",),
    installer_markers_match_all=True,
    installer_markers=["quarto-", "linux-amd64.tar.gz"],
    href_exclude_substrings=["arm64", "aarch64", ".deb", ".rpm", "win", "macos", "checksum"],
    installer_extensions=[".tar.gz"],
)
_desk(
    "tectonic-typesetting/tectonic",
    "03-写作.json",
    "写作",
    "Tectonic（现代 TeX 引擎，免装 TeX Live）",
    id="tectonic",
    plats=("windows",),
    installer_markers_match_all=True,
    installer_markers=["tectonic-", "x86_64-pc-windows-msvc.zip"],
    href_exclude_substrings=["gnu", "linux", "apple", "AppImage", "arm"],
    installer_extensions=[".zip"],
)
_desk(
    "tectonic-typesetting/tectonic",
    "03-写作.json",
    "写作",
    "Tectonic（现代 TeX 引擎；macOS Apple Silicon）",
    id="tectonic",
    plats=("darwin",),
    installer_markers_match_all=True,
    installer_markers=["tectonic-", "aarch64-apple-darwin.tar.gz"],
    href_exclude_substrings=["x86_64", "linux", "windows", "AppImage"],
    installer_extensions=[".tar.gz"],
)
_desk(
    "tectonic-typesetting/tectonic",
    "03-写作.json",
    "写作",
    "Tectonic（现代 TeX 引擎；Linux x86_64 musl）",
    id="tectonic",
    plats=("linux",),
    installer_markers_match_all=True,
    installer_markers=["tectonic-", "x86_64-unknown-linux-musl.tar.gz"],
    href_exclude_substrings=["gnu", "apple", "windows", "AppImage", "arm", "i686"],
    installer_extensions=[".tar.gz"],
)
_open_page(
    "zotero/zotero",
    "03-写作.json",
    "写作",
    "Zotero（文献管理；官方不走 GitHub Assets，请打开 Releases/官网）",
    id="zotero",
)

# --- 04 办公 ---
_desk(
    "pdfcpu/pdfcpu",
    "04-办公.json",
    "办公",
    "pdfcpu（PDF 工具箱：合并/拆分/水印/优化）",
    id="pdfcpu",
    plats=("windows",),
    installer_markers_match_all=True,
    installer_markers=["pdfcpu_", "Windows_x86_64.zip"],
    href_exclude_substrings=["win7", "i386", "Darwin", "Linux", "checksum", "Js_wasm"],
    installer_extensions=[".zip"],
)
_desk(
    "pdfcpu/pdfcpu",
    "04-办公.json",
    "办公",
    "pdfcpu（PDF 工具箱；macOS Apple Silicon）",
    id="pdfcpu",
    plats=("darwin",),
    installer_markers_match_all=True,
    installer_markers=["pdfcpu_", "Darwin_arm64.tar.xz"],
    href_exclude_substrings=["x86_64", "Windows", "Linux", "checksum"],
    installer_extensions=[".tar.xz"],
)
_desk(
    "pdfcpu/pdfcpu",
    "04-办公.json",
    "办公",
    "pdfcpu（PDF 工具箱；Linux x86_64）",
    id="pdfcpu",
    plats=("linux",),
    installer_markers_match_all=True,
    installer_markers=["pdfcpu_", "Linux_x86_64.tar.xz"],
    href_exclude_substrings=["arm", "i386", "Windows", "Darwin", "checksum"],
    installer_extensions=[".tar.xz"],
)

# --- 07 备份 ---
_desk(
    "uroni/urbackup_backend",
    "07-备份.json",
    "备份",
    "UrBackup Server（客户端/服务端镜像与文件备份）",
    id="urbackup_server",
    plats=("windows",),
    installer_markers_match_all=True,
    installer_markers=["UrBackup.Server.", "x64.msi"],
    href_exclude_substrings=[".deb", ".tar.gz", ".exe"],
    installer_extensions=[".msi"],
    windows_installer=True,
    run_installer=True,
)
_desk(
    "uroni/urbackup_backend",
    "07-备份.json",
    "备份",
    "UrBackup Server（Linux amd64 deb）",
    id="urbackup_server",
    plats=("linux",),
    installer_markers_match_all=True,
    installer_markers=["urbackup-server_", "amd64.deb"],
    href_exclude_substrings=["dbg", "arm", ".exe", ".msi", ".tar.gz"],
    installer_extensions=[".deb"],
)
_open_page(
    "uroni/urbackup_backend",
    "07-备份.json",
    "备份",
    "UrBackup Server（仅 Windows/Linux 包；macOS 请打开 Releases 页）",
    id="urbackup_server",
    plats=("darwin",),
)
_desk(
    "borgbackup/borg",
    "07-备份.json",
    "备份",
    "BorgBackup（去重加密备份；Linux 独立二进制）",
    id="borg",
    plats=("linux",),
    installer_markers_match_all=True,
    installer_markers=["borg-linux-glibc236"],
    href_exclude_substrings=[".asc", ".tgz", "freebsd", "macos", ".tar.gz", "README"],
    installer_extensions=[],
    use_download_filename=True,
)
_desk(
    "borgbackup/borg",
    "07-备份.json",
    "备份",
    "BorgBackup（去重加密备份；macOS 独立二进制）",
    id="borg",
    plats=("darwin",),
    installer_markers=["borg-macos1012"],
    href_exclude_substrings=[".asc", ".tgz", "linux", "freebsd", ".tar.gz", "README"],
)
_open_page(
    "borgbackup/borg",
    "07-备份.json",
    "备份",
    "BorgBackup（Windows 支持有限；请打开 Releases 页）",
    id="borg",
    plats=("windows",),
)

# --- 19 网络与协作 ---
_desk(
    "jitsi/jitsi-meet-electron",
    "19-网络与协作.json",
    "网络与协作",
    "Jitsi Meet（开源视频会议桌面端）",
    id="jitsi_meet_electron",
    plats=("windows",),
    installer_markers=["jitsi-meet.exe"],
    href_exclude_substrings=[".blockmap", ".dmg", ".deb", "AppImage", ".yml", ".zip"],
    installer_extensions=[".exe"],
    windows_installer=True,
    run_installer=True,
)
_desk(
    "jitsi/jitsi-meet-electron",
    "19-网络与协作.json",
    "网络与协作",
    "Jitsi Meet（开源视频会议桌面端；macOS DMG）",
    id="jitsi_meet_electron",
    plats=("darwin",),
    installer_markers=["jitsi-meet.dmg"],
    href_exclude_substrings=[".blockmap", ".exe", ".deb", "AppImage", ".yml"],
    installer_extensions=[".dmg"],
)
_desk(
    "jitsi/jitsi-meet-electron",
    "19-网络与协作.json",
    "网络与协作",
    "Jitsi Meet（开源视频会议桌面端；Linux AppImage）",
    id="jitsi_meet_electron",
    plats=("linux",),
    installer_markers=["jitsi-meet-x86_64.AppImage"],
    href_exclude_substrings=["arm64", ".deb", ".exe", ".dmg", ".yml", ".blockmap"],
    installer_extensions=[".AppImage"],
)

# --- 20 网络与通讯 ---
_desk(
    "session-foundation/session-desktop",
    "20-网络与通讯.json",
    "网络与通讯",
    "Session Desktop（去中心化隐私即时通讯）",
    id="session_desktop",
    plats=("windows",),
    installer_markers_match_all=True,
    installer_markers=["session-desktop-win-x64-", ".exe"],
    href_exclude_substrings=[".blockmap", ".yml", ".asc", "mac", "linux"],
    installer_extensions=[".exe"],
    windows_installer=True,
    run_installer=True,
)
_desk(
    "session-foundation/session-desktop",
    "20-网络与通讯.json",
    "网络与通讯",
    "Session Desktop（去中心化隐私即时通讯；macOS Apple Silicon）",
    id="session_desktop",
    plats=("darwin",),
    installer_markers_match_all=True,
    installer_markers=["session-desktop-mac-arm64-", ".dmg"],
    href_exclude_substrings=[".blockmap", ".zip", "x64", "win", "linux"],
    installer_extensions=[".dmg"],
)
_desk(
    "session-foundation/session-desktop",
    "20-网络与通讯.json",
    "网络与通讯",
    "Session Desktop（去中心化隐私即时通讯；Linux AppImage）",
    id="session_desktop",
    plats=("linux",),
    installer_markers_match_all=True,
    installer_markers=["session-desktop-linux-x86_64-", ".AppImage"],
    href_exclude_substrings=[".deb", ".rpm", "freebsd", "win", "mac"],
    installer_extensions=[".AppImage"],
)
_desk(
    "deltachat/deltachat-desktop",
    "20-网络与通讯.json",
    "网络与通讯",
    "Delta Chat（基于邮件协议的加密聊天）",
    id="deltachat_desktop",
    plats=("windows",),
    installer_markers_match_all=True,
    installer_markers=["DeltaChat-", "Setup.x64.exe"],
    href_exclude_substrings=["Portable", "tauri", "AppImage", ".dmg", ".deb", ".rpm", ".msi"],
    installer_extensions=[".exe"],
    windows_installer=True,
    run_installer=True,
)
_desk(
    "deltachat/deltachat-desktop",
    "20-网络与通讯.json",
    "网络与通讯",
    "Delta Chat（基于邮件协议的加密聊天；macOS universal DMG）",
    id="deltachat_desktop",
    plats=("darwin",),
    installer_markers_match_all=True,
    installer_markers=["DeltaChat-", "universal.dmg"],
    href_exclude_substrings=["tauri", "arm64.dmg", "AppImage", ".exe", ".deb"],
    installer_extensions=[".dmg"],
)
_desk(
    "deltachat/deltachat-desktop",
    "20-网络与通讯.json",
    "网络与通讯",
    "Delta Chat（基于邮件协议的加密聊天；Linux AppImage）",
    id="deltachat_desktop",
    plats=("linux",),
    installer_markers_match_all=True,
    installer_markers=["DeltaChat-", "x86_64.AppImage"],
    href_exclude_substrings=["arm64", "tauri", ".deb", ".rpm", ".exe", ".dmg"],
    installer_extensions=[".AppImage"],
)

# --- 21 远程与协作 ---
_desk(
    "deskflow/deskflow",
    "21-远程与协作.json",
    "远程与协作",
    "Deskflow（跨机键鼠共享，Barrier/Input Leap 继任）",
    id="deskflow",
    plats=("windows",),
    installer_markers_match_all=True,
    installer_markers=["deskflow-", "win-x64.msi"],
    href_exclude_substrings=["portable", "arm64", ".7z", ".dmg", ".deb", ".rpm", "flatpak"],
    installer_extensions=[".msi"],
    windows_installer=True,
    run_installer=True,
)
_desk(
    "deskflow/deskflow",
    "21-远程与协作.json",
    "远程与协作",
    "Deskflow（跨机键鼠共享；macOS Apple Silicon）",
    id="deskflow",
    plats=("darwin",),
    installer_markers_match_all=True,
    installer_markers=["deskflow-", "macos-arm64.dmg"],
    href_exclude_substrings=["x86_64", "win", ".deb", ".rpm", "flatpak"],
    installer_extensions=[".dmg"],
)
_desk(
    "deskflow/deskflow",
    "21-远程与协作.json",
    "远程与协作",
    "Deskflow（跨机键鼠共享；Linux x86_64 flatpak）",
    id="deskflow",
    plats=("linux",),
    installer_markers_match_all=True,
    installer_markers=["deskflow-", "linux-x86_64.flatpak"],
    href_exclude_substrings=["aarch64", "win", ".dmg", ".deb", ".rpm", "sums"],
    installer_extensions=[".flatpak"],
)
_open_page(
    "TigerVNC/tigervnc",
    "21-远程与协作.json",
    "远程与协作",
    "TigerVNC（开源 VNC；GitHub 无 Assets，请打开 Releases/官网）",
    id="tigervnc",
)
_open_page(
    "input-leap/input-leap",
    "21-远程与协作.json",
    "远程与协作",
    "Input Leap（Barrier 分支；当前多为调试包，请打开 Releases 页）",
    id="input_leap",
)

# --- 22 音视频 ---
_desk(
    "olive-editor/olive",
    "22-音视频.json",
    "音视频",
    "Olive（开源非线性视频剪辑；钉选 0.2.0-nightly）",
    id="olive",
    plats=("windows",),
    pinned_release_tag="0.2.0-nightly",
    installer_markers_match_all=True,
    installer_markers=["Olive-", "Windows-x86_64.exe"],
    href_exclude_substrings=["Portable", "AppImage", ".dmg", "Linux", "macOS"],
    installer_extensions=[".exe"],
    windows_installer=True,
    run_installer=True,
)
_desk(
    "olive-editor/olive",
    "22-音视频.json",
    "音视频",
    "Olive（开源非线性视频剪辑；macOS Apple Silicon；钉选 0.2.0-nightly）",
    id="olive",
    plats=("darwin",),
    pinned_release_tag="0.2.0-nightly",
    installer_markers_match_all=True,
    installer_markers=["Olive-", "macOS-arm64.dmg"],
    href_exclude_substrings=["x86_64", "Windows", "Linux", "AppImage"],
    installer_extensions=[".dmg"],
)
_desk(
    "olive-editor/olive",
    "22-音视频.json",
    "音视频",
    "Olive（开源非线性视频剪辑；Linux AppImage；钉选 0.2.0-nightly）",
    id="olive",
    plats=("linux",),
    pinned_release_tag="0.2.0-nightly",
    installer_markers_match_all=True,
    installer_markers=["Olive-", "Linux-x86_64.AppImage"],
    href_exclude_substrings=["Windows", "macOS", ".exe", ".dmg"],
    installer_extensions=[".AppImage"],
)

# --- 25 可观测 ---
_desk(
    "VictoriaMetrics/VictoriaMetrics",
    "25-可观测.json",
    "可观测",
    "VictoriaMetrics（高性能 Prometheus 兼容时序库；单机 Windows）",
    id="victoria_metrics",
    plats=("windows",),
    installer_markers_match_all=True,
    installer_markers=["victoria-metrics-windows-amd64-", ".zip"],
    href_exclude_substrings=["cluster", "enterprise", "checksum", "vmutils"],
    installer_extensions=[".zip"],
)
_desk(
    "VictoriaMetrics/VictoriaMetrics",
    "25-可观测.json",
    "可观测",
    "VictoriaMetrics（高性能 Prometheus 兼容时序库；单机 Linux）",
    id="victoria_metrics",
    plats=("linux",),
    installer_markers_match_all=True,
    installer_markers=["victoria-metrics-linux-amd64-", ".tar.gz"],
    href_exclude_substrings=["cluster", "enterprise", "checksum", "vmutils", "arm"],
    installer_extensions=[".tar.gz"],
)
_desk(
    "VictoriaMetrics/VictoriaMetrics",
    "25-可观测.json",
    "可观测",
    "VictoriaMetrics（高性能 Prometheus 兼容时序库；单机 macOS Apple Silicon）",
    id="victoria_metrics",
    plats=("darwin",),
    installer_markers_match_all=True,
    installer_markers=["victoria-metrics-darwin-arm64-", ".tar.gz"],
    href_exclude_substrings=["cluster", "enterprise", "checksum", "vmutils", "amd64"],
    installer_extensions=[".tar.gz"],
)
_desk(
    "open-telemetry/opentelemetry-collector-releases",
    "25-可观测.json",
    "可观测",
    "OpenTelemetry Collector（otelcol 官方发行）",
    id="otelcol",
    plats=("windows",),
    installer_markers_match_all=True,
    installer_markers=["otelcol_", "windows_amd64.tar.gz"],
    href_exclude_substrings=["contrib", "k8s", "otlp", "checksum", ".pem", ".sig", ".sbom", "386"],
    installer_extensions=[".tar.gz"],
)
_desk(
    "open-telemetry/opentelemetry-collector-releases",
    "25-可观测.json",
    "可观测",
    "OpenTelemetry Collector（otelcol；Linux amd64）",
    id="otelcol",
    plats=("linux",),
    installer_markers_match_all=True,
    installer_markers=["otelcol_", "linux_amd64.tar.gz"],
    href_exclude_substrings=["contrib", "k8s", "otlp", "checksum", ".pem", ".sig", ".sbom", ".deb", ".rpm", "arm"],
    installer_extensions=[".tar.gz"],
)
_desk(
    "open-telemetry/opentelemetry-collector-releases",
    "25-可观测.json",
    "可观测",
    "OpenTelemetry Collector（otelcol；macOS Apple Silicon）",
    id="otelcol",
    plats=("darwin",),
    installer_markers_match_all=True,
    installer_markers=["otelcol_", "darwin_arm64.tar.gz"],
    href_exclude_substrings=["contrib", "k8s", "otlp", "checksum", ".pem", ".sig", ".sbom", "amd64"],
    installer_extensions=[".tar.gz"],
)
_desk(
    "netdata/netdata",
    "25-可观测.json",
    "可观测",
    "Netdata（实时系统监控 Agent；Windows MSI）",
    id="netdata",
    plats=("windows",),
    installer_markers=["netdata-x64.msi"],
    href_exclude_substrings=[".deb", ".rpm", "linux", "checksum"],
    installer_extensions=[".msi"],
    windows_installer=True,
    run_installer=True,
)
_open_page(
    "netdata/netdata",
    "25-可观测.json",
    "可观测",
    "Netdata（实时系统监控；非 Windows 请打开 Releases/官网安装）",
    id="netdata",
    plats=("linux", "darwin"),
)

# --- 27 金融与股票 ---
_desk(
    "Gnucash/gnucash",
    "27-金融与股票.json",
    "金融与股票",
    "GnuCash（复式记账/个人理财）",
    id="gnucash",
    plats=("windows",),
    installer_markers_match_all=True,
    installer_markers=["gnucash-", ".setup.exe"],
    href_exclude_substrings=[".tar.", "docs", ".dmg"],
    installer_extensions=[".exe"],
    windows_installer=True,
    run_installer=True,
)
_desk(
    "Gnucash/gnucash",
    "27-金融与股票.json",
    "金融与股票",
    "GnuCash（复式记账；macOS Apple Silicon）",
    id="gnucash",
    plats=("darwin",),
    installer_markers_match_all=True,
    installer_markers=["Gnucash-Arm-", ".dmg"],
    href_exclude_substrings=["Intel", ".exe", ".tar."],
    installer_extensions=[".dmg"],
)
_open_page(
    "Gnucash/gnucash",
    "27-金融与股票.json",
    "金融与股票",
    "GnuCash（Linux 请用发行版包或打开 Releases 页）",
    id="gnucash",
    plats=("linux",),
)
_desk(
    "simonmichael/hledger",
    "27-金融与股票.json",
    "金融与股票",
    "hledger（纯文本复式记账 CLI）",
    id="hledger",
    plats=("windows",),
    installer_markers=["hledger-windows-x64.zip"],
    href_exclude_substrings=["linux", "mac"],
    installer_extensions=[".zip"],
)
_desk(
    "simonmichael/hledger",
    "27-金融与股票.json",
    "金融与股票",
    "hledger（纯文本复式记账 CLI；macOS Apple Silicon）",
    id="hledger",
    plats=("darwin",),
    installer_markers=["hledger-mac-arm64.tar.gz"],
    href_exclude_substrings=["x64", "windows", "linux"],
    installer_extensions=[".tar.gz"],
)
_desk(
    "simonmichael/hledger",
    "27-金融与股票.json",
    "金融与股票",
    "hledger（纯文本复式记账 CLI；Linux x64）",
    id="hledger",
    plats=("linux",),
    installer_markers=["hledger-linux-x64.tar.gz"],
    href_exclude_substrings=["mac", "windows"],
    installer_extensions=[".tar.gz"],
)
_open_page(
    "freqtrade/freqtrade",
    "27-金融与股票.json",
    "金融与股票",
    "Freqtrade（量化交易机器人；以 Docker/源码为主，请打开 Releases 页）",
    id="freqtrade",
)

# --- 30 代理与隧道 ---
_desk(
    "XTLS/Xray-core",
    "30-代理与隧道.json",
    "代理与隧道",
    "Xray-core（代理内核）",
    id="xray_core",
    plats=("windows",),
    installer_markers=["Xray-windows-64.zip"],
    href_exclude_substrings=[".dgst", "win7", "32", "arm64", "android", "linux", "macos", "freebsd"],
    installer_extensions=[".zip"],
)
_desk(
    "XTLS/Xray-core",
    "30-代理与隧道.json",
    "代理与隧道",
    "Xray-core（代理内核；Linux 64）",
    id="xray_core",
    plats=("linux",),
    installer_markers=["Xray-linux-64.zip"],
    href_exclude_substrings=[".dgst", "arm", "32", "android", "windows", "macos", "freebsd", "riscv", "loong"],
    installer_extensions=[".zip"],
)
_desk(
    "XTLS/Xray-core",
    "30-代理与隧道.json",
    "代理与隧道",
    "Xray-core（代理内核；macOS Apple Silicon）",
    id="xray_core",
    plats=("darwin",),
    installer_markers=["Xray-macos-arm64-v8a.zip"],
    href_exclude_substrings=[".dgst", "64.zip", "windows", "linux", "android"],
    installer_extensions=[".zip"],
)
_desk(
    "MatsuriDayo/nekoray",
    "30-代理与隧道.json",
    "代理与隧道",
    "NekoRay/NekoBox（Qt 图形代理客户端，sing-box 核心）",
    id="nekoray",
    plats=("windows",),
    installer_markers_match_all=True,
    installer_markers=["nekoray-", "windows64.zip"],
    href_exclude_substrings=["linux", ".deb", "AppImage"],
    installer_extensions=[".zip"],
)
_desk(
    "MatsuriDayo/nekoray",
    "30-代理与隧道.json",
    "代理与隧道",
    "NekoRay/NekoBox（Linux AppImage）",
    id="nekoray",
    plats=("linux",),
    installer_markers_match_all=True,
    installer_markers=["nekoray-", "linux-x64.AppImage"],
    href_exclude_substrings=["windows", ".deb", ".zip"],
    installer_extensions=[".AppImage"],
)
_open_page(
    "MatsuriDayo/nekoray",
    "30-代理与隧道.json",
    "代理与隧道",
    "NekoRay（已不支持旧版 macOS；请打开 Releases 页）",
    id="nekoray",
    plats=("darwin",),
)
_desk(
    "fatedier/frp",
    "30-代理与隧道.json",
    "代理与隧道",
    "frp（内网穿透 frpc/frps）",
    id="frp",
    plats=("windows",),
    installer_markers_match_all=True,
    installer_markers=["frp_", "windows_amd64.zip"],
    href_exclude_substrings=["arm64", "linux", "darwin", "checksum", "freebsd"],
    installer_extensions=[".zip"],
)
_desk(
    "fatedier/frp",
    "30-代理与隧道.json",
    "代理与隧道",
    "frp（内网穿透；Linux amd64）",
    id="frp",
    plats=("linux",),
    installer_markers_match_all=True,
    installer_markers=["frp_", "linux_amd64.tar.gz"],
    href_exclude_substrings=["arm", "darwin", "windows", "checksum", "mips", "riscv", "loong"],
    installer_extensions=[".tar.gz"],
)
_desk(
    "fatedier/frp",
    "30-代理与隧道.json",
    "代理与隧道",
    "frp（内网穿透；macOS Apple Silicon）",
    id="frp",
    plats=("darwin",),
    installer_markers_match_all=True,
    installer_markers=["frp_", "darwin_arm64.tar.gz"],
    href_exclude_substrings=["amd64", "windows", "linux", "checksum"],
    installer_extensions=[".tar.gz"],
)
_desk(
    "shadowsocks/shadowsocks-rust",
    "30-代理与隧道.json",
    "代理与隧道",
    "shadowsocks-rust（Shadowsocks 官方 Rust 实现）",
    id="shadowsocks_rust",
    plats=("windows",),
    installer_markers_match_all=True,
    installer_markers=["shadowsocks-", "x86_64-pc-windows-msvc.zip"],
    href_exclude_substrings=[".sha256", "gnu", "linux", "apple", "android"],
    installer_extensions=[".zip"],
)
_desk(
    "shadowsocks/shadowsocks-rust",
    "30-代理与隧道.json",
    "代理与隧道",
    "shadowsocks-rust（Linux x86_64 musl）",
    id="shadowsocks_rust",
    plats=("linux",),
    installer_markers_match_all=True,
    installer_markers=["shadowsocks-", "x86_64-unknown-linux-musl.tar.xz"],
    href_exclude_substrings=[".sha256", "gnu", "android", "windows", "apple", "arm"],
    installer_extensions=[".tar.xz"],
)
_desk(
    "shadowsocks/shadowsocks-rust",
    "30-代理与隧道.json",
    "代理与隧道",
    "shadowsocks-rust（macOS Apple Silicon）",
    id="shadowsocks_rust",
    plats=("darwin",),
    installer_markers_match_all=True,
    installer_markers=["shadowsocks-", "aarch64-apple-darwin.tar.xz"],
    href_exclude_substrings=[".sha256", "x86_64", "linux", "windows", "android"],
    installer_extensions=[".tar.xz"],
)
_desk(
    "GUI-for-Cores/GUI.for.SingBox",
    "30-代理与隧道.json",
    "代理与隧道",
    "GUI.for.SingBox（sing-box 图形前端）",
    id="gui_for_singbox",
    plats=("windows",),
    installer_markers=["GUI.for.SingBox-windows-amd64.zip"],
    href_exclude_substrings=["arm64", "386", "linux", "darwin"],
    installer_extensions=[".zip"],
)
_desk(
    "GUI-for-Cores/GUI.for.SingBox",
    "30-代理与隧道.json",
    "代理与隧道",
    "GUI.for.SingBox（sing-box 图形前端；Linux）",
    id="gui_for_singbox",
    plats=("linux",),
    installer_markers=["GUI.for.SingBox-linux-amd64.zip"],
    href_exclude_substrings=["windows", "darwin", "arm64"],
    installer_extensions=[".zip"],
)
_desk(
    "GUI-for-Cores/GUI.for.SingBox",
    "30-代理与隧道.json",
    "代理与隧道",
    "GUI.for.SingBox（sing-box 图形前端；macOS Apple Silicon）",
    id="gui_for_singbox",
    plats=("darwin",),
    installer_markers=["GUI.for.SingBox-darwin-arm64.zip"],
    href_exclude_substrings=["amd64", "windows", "linux"],
    installer_extensions=[".zip"],
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
