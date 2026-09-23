#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Batch29：桌面分类缺口（GitHub Release 有官方安装包）+ Android Karing。"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS = os.path.join(ROOT, "apps")
MOBILE = os.path.join(ROOT, "apps-mobile")
BATCH: dict[tuple[str, str], list] = {}
MOBILE_BATCH: dict[str, list] = {}


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
SH_OFF = "04-办公.json"
SH_BAK = "07-备份.json"
SH_DEV = "12-开发.json"
SH_EFF = "13-效率.json"
SH_GAME = "14-游戏.json"
SH_TERM = "17-终端.json"
SH_NET = "18-网络.json"
SH_COLLAB = "19-网络与协作.json"
SH_IM = "20-网络与通讯.json"
SH_DB = "23-数据库.json"
SH_CN = "24-云原生.json"
SH_OBS = "25-可观测.json"
SH_FIN = "27-金融与股票.json"
SH_LAN = "29-局域网文件共享.json"
SH_PROXY = "30-代理与隧道.json"

# --- 下载：N_m3u8DL-RE（CLI 后继，跨平台官方包） ---
_e("windows", SH_DL, "n_m3u8dl_re",
   "N_m3u8DL-RE（nilaoda m3u8/流媒体下载；Windows x64 zip，CLI 后继）", "下载",
   "nilaoda/N_m3u8DL-RE",
   installer_markers_match_all=True,
   installer_markers=["N_m3u8DL-RE_", "win-x64_", ".zip"],
   href_exclude_substrings=_ex("arm64", "NT6", "linux", "osx", "android"),
   installer_extensions=[".zip"],
   aliases=["n_m3u8dl_re", "N_m3u8DL-RE", "m3u8dl-re", "m3u8下载"])
_e("darwin", SH_DL, "n_m3u8dl_re",
   "N_m3u8DL-RE（nilaoda m3u8/流媒体下载；macOS Apple Silicon tar.gz）", "下载",
   "nilaoda/N_m3u8DL-RE",
   installer_markers_match_all=True,
   installer_markers=["N_m3u8DL-RE_", "osx-arm64_", ".tar.gz"],
   href_exclude_substrings=_ex("osx-x64", "linux", "win-", "android"),
   installer_extensions=[".tar.gz"],
   aliases=["n_m3u8dl_re", "N_m3u8DL-RE", "m3u8dl-re"])
_e("linux", SH_DL, "n_m3u8dl_re",
   "N_m3u8DL-RE（nilaoda m3u8/流媒体下载；Linux x64 tar.gz）", "下载",
   "nilaoda/N_m3u8DL-RE",
   installer_markers_match_all=True,
   installer_markers=["N_m3u8DL-RE_", "linux-x64_", ".tar.gz"],
   href_exclude_substrings=_ex("linux-arm64", "osx", "win-", "android"),
   installer_extensions=[".tar.gz"],
   aliases=["n_m3u8dl_re", "N_m3u8DL-RE", "m3u8dl-re"])

# --- 办公：JabRef ---
_e("windows", SH_OFF, "jabref",
   "JabRef（开源文献/BibTeX 管理；Windows MSI）", "办公",
   "JabRef/jabref",
   installer_markers_match_all=True,
   installer_markers=["JabRef-", ".msi"],
   href_exclude_substrings=_ex("portable", "dmg", "pkg", "linux", "arm64"),
   installer_extensions=[".msi"], windows_installer=True, run_installer=True,
   process_name="JabRef.exe", kill_before_install=True,
   aliases=["jabref", "JabRef", "文献管理", "bibtex"])
_e("darwin", SH_OFF, "jabref",
   "JabRef（开源文献/BibTeX 管理；macOS Apple Silicon dmg）", "办公",
   "JabRef/jabref",
   installer_markers_match_all=True,
   installer_markers=["JabRef-", "-arm64.dmg"],
   href_exclude_substrings=_ex("portable", ".pkg", "windows", ".msi"),
   installer_extensions=[".dmg"],
   aliases=["jabref", "JabRef", "文献管理"])
_e("linux", SH_OFF, "jabref",
   "JabRef（开源文献/BibTeX 管理；Debian amd64 deb）", "办公",
   "JabRef/jabref",
   installer_markers_match_all=True,
   installer_markers=["jabref_", "_amd64.deb"],
   href_exclude_substrings=_ex("rpm", "portable", "windows", "dmg"),
   installer_extensions=[".deb"],
   aliases=["jabref", "JabRef", "文献管理"])

# --- 备份：Backrest / Vorta ---
_e("windows", SH_BAK, "backrest",
   "Backrest（restic Web UI 备份；Windows x64 安装包）", "备份",
   "garethgeorge/backrest",
   installer_markers_match_all=True,
   installer_markers=["BackrestSetup-x86_64.exe"],
   href_exclude_substrings=_ex("arm64", "Darwin", "Linux", ".zip"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["backrest", "Backrest", "restic ui", "restic图形"])
_e("darwin", SH_BAK, "backrest",
   "Backrest（restic Web UI 备份；macOS Apple Silicon tar.gz）", "备份",
   "garethgeorge/backrest",
   installer_markers_match_all=True,
   installer_markers=["backrest_Darwin_arm64.tar.gz"],
   href_exclude_substrings=_ex("x86_64", "Linux", "Windows", ".zip"),
   installer_extensions=[".tar.gz"],
   aliases=["backrest", "Backrest", "restic ui"])
_e("linux", SH_BAK, "backrest",
   "Backrest（restic Web UI 备份；Linux x86_64 tar.gz）", "备份",
   "garethgeorge/backrest",
   installer_markers_match_all=True,
   installer_markers=["backrest_Linux_x86_64.tar.gz"],
   href_exclude_substrings=_ex("arm", "Darwin", "Windows", "i386"),
   installer_extensions=[".tar.gz"],
   aliases=["backrest", "Backrest", "restic ui"])
_e("darwin", SH_BAK, "vorta",
   "Vorta（Borg 备份图形前端；macOS Apple Silicon dmg）", "备份",
   "borgbase/vorta",
   installer_markers_match_all=True,
   installer_markers=["Vorta-", "-arm.dmg"],
   href_exclude_substrings=_ex("intel", "x86"),
   installer_extensions=[".dmg"],
   aliases=["vorta", "Vorta", "borg gui", "borg备份"])

# --- 网络与协作：Revolt ---
_e("windows", SH_COLLAB, "revolt_desktop",
   "Revolt（开源 Discord 风格聊天；Windows Setup）", "网络与协作",
   "revoltchat/desktop",
   installer_markers_match_all=True,
   installer_markers=["Revolt-Setup-", ".exe"],
   href_exclude_substrings=_ex("arm64", "mac", "linux", ".zip"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   process_name="Revolt.exe", kill_before_install=True,
   aliases=["revolt", "Revolt", "revolt.chat"])
_e("darwin", SH_COLLAB, "revolt_desktop",
   "Revolt（开源 Discord 风格聊天；macOS universal dmg）", "网络与协作",
   "revoltchat/desktop",
   installer_markers_match_all=True,
   installer_markers=["Revolt-", "-universal.dmg"],
   href_exclude_substrings=_ex(".zip", "AppImage", "windows"),
   installer_extensions=[".dmg"],
   aliases=["revolt", "Revolt", "revolt.chat"])
_e("linux", SH_COLLAB, "revolt_desktop",
   "Revolt（开源 Discord 风格聊天；Linux x64 AppImage）", "网络与协作",
   "revoltchat/desktop",
   installer_markers_match_all=True,
   installer_markers=["Revolt-", ".AppImage"],
   href_exclude_substrings=_ex("arm64", "armv7l", "windows", "mac"),
   installer_extensions=[".AppImage"],
   aliases=["revolt", "Revolt", "revolt.chat"])

# --- 金融：Portfolio Performance / Wealthfolio ---
_e("windows", SH_FIN, "portfolio_performance",
   "Portfolio Performance（开源投资组合跟踪；Windows Setup）", "金融与股票",
   "portfolio-performance/portfolio",
   installer_markers_match_all=True,
   installer_markers=["PortfolioPerformance-", "-setup.exe"],
   href_exclude_substrings=_ex(".zip", "linux", "dmg", "distro"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   process_name="PortfolioPerformance.exe", kill_before_install=True,
   aliases=["portfolio performance", "Portfolio Performance", "投资组合", "pp"])
_e("darwin", SH_FIN, "portfolio_performance",
   "Portfolio Performance（开源投资组合跟踪；macOS Apple Silicon dmg）", "金融与股票",
   "portfolio-performance/portfolio",
   installer_markers_match_all=True,
   installer_markers=["PortfolioPerformance-", "-aarch64.dmg"],
   href_exclude_substrings=_ex("x86_64", "linux", "windows", ".zip"),
   installer_extensions=[".dmg"],
   aliases=["portfolio performance", "Portfolio Performance", "投资组合"])
_e("linux", SH_FIN, "portfolio_performance",
   "Portfolio Performance（开源投资组合跟踪；Linux x86_64 tar.gz）", "金融与股票",
   "portfolio-performance/portfolio",
   installer_markers_match_all=True,
   installer_markers=["PortfolioPerformance-", "-linux.gtk.x86_64.tar.gz"],
   href_exclude_substrings=_ex("aarch64", "windows", "dmg", "distro"),
   installer_extensions=[".tar.gz"],
   aliases=["portfolio performance", "Portfolio Performance", "投资组合"])
_e("windows", SH_FIN, "wealthfolio",
   "Wealthfolio（本地优先投资组合桌面；Windows x64 Setup）", "金融与股票",
   "afadil/wealthfolio",
   installer_markers_match_all=True,
   installer_markers=["Wealthfolio_", "_x64-setup.exe"],
   href_exclude_substrings=_ex("arm64", "machine", "nsis", ".msi"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   process_name="Wealthfolio.exe", kill_before_install=True,
   aliases=["wealthfolio", "Wealthfolio", "财富组合"])
_e("darwin", SH_FIN, "wealthfolio",
   "Wealthfolio（本地优先投资组合桌面；macOS Apple Silicon dmg）", "金融与股票",
   "afadil/wealthfolio",
   installer_markers_match_all=True,
   installer_markers=["Wealthfolio_", "_aarch64.dmg"],
   href_exclude_substrings=_ex("x64", ".app.tar.gz", "windows", "linux"),
   installer_extensions=[".dmg"],
   aliases=["wealthfolio", "Wealthfolio"])
_e("linux", SH_FIN, "wealthfolio",
   "Wealthfolio（本地优先投资组合桌面；Debian amd64 deb）", "金融与股票",
   "afadil/wealthfolio",
   installer_markers_match_all=True,
   installer_markers=["Wealthfolio_", "_amd64.deb"],
   href_exclude_substrings=_ex("arm64", "AppImage", "rpm", "windows"),
   installer_extensions=[".deb"],
   aliases=["wealthfolio", "Wealthfolio"])

# --- 数据库：DbGate ---
_e("windows", SH_DB, "dbgate",
   "DbGate（开源多数据库桌面客户端；Windows x64）", "数据库",
   "dbgate/dbgate",
   installer_markers_match_all=True,
   installer_markers=["dbgate-", "-win_x64.exe"],
   href_exclude_substrings=_ex("premium", "latest", "arm64", ".zip"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   process_name="dbgate.exe", kill_before_install=True,
   aliases=["dbgate", "DbGate", "数据库客户端"])
_e("darwin", SH_DB, "dbgate",
   "DbGate（开源多数据库桌面客户端；macOS Apple Silicon dmg）", "数据库",
   "dbgate/dbgate",
   installer_markers_match_all=True,
   installer_markers=["dbgate-", "-mac_arm64.dmg"],
   href_exclude_substrings=_ex("premium", "latest", "universal", "x64", ".zip"),
   installer_extensions=[".dmg"],
   aliases=["dbgate", "DbGate"])
_e("linux", SH_DB, "dbgate",
   "DbGate（开源多数据库桌面客户端；Debian amd64 deb）", "数据库",
   "dbgate/dbgate",
   installer_markers_match_all=True,
   installer_markers=["dbgate-", "-linux_amd64.deb"],
   href_exclude_substrings=_ex("premium", "latest", "arm64", "AppImage"),
   installer_extensions=[".deb"],
   aliases=["dbgate", "DbGate"])

# --- 可观测：Beszel / k6 ---
_e("windows", SH_OBS, "beszel",
   "Beszel（轻量服务器监控 Hub；Windows amd64 zip）", "可观测",
   "henrygd/beszel",
   installer_markers_match_all=True,
   installer_markers=["beszel_windows_amd64.zip"],
   href_exclude_substrings=_ex("agent", "arm64"),
   installer_extensions=[".zip"],
   aliases=["beszel", "Beszel", "服务器监控"])
_e("darwin", SH_OBS, "beszel",
   "Beszel（轻量服务器监控 Hub；macOS Apple Silicon tar.gz）", "可观测",
   "henrygd/beszel",
   installer_markers_match_all=True,
   installer_markers=["beszel_darwin_arm64.tar.gz"],
   href_exclude_substrings=_ex("agent", "amd64"),
   installer_extensions=[".tar.gz"],
   aliases=["beszel", "Beszel"])
_e("linux", SH_OBS, "beszel",
   "Beszel（轻量服务器监控 Hub；Linux amd64 tar.gz）", "可观测",
   "henrygd/beszel",
   installer_markers_match_all=True,
   installer_markers=["beszel_linux_amd64.tar.gz"],
   href_exclude_substrings=_ex("agent", "arm"),
   installer_extensions=[".tar.gz"],
   aliases=["beszel", "Beszel"])
_e("windows", SH_OBS, "k6",
   "k6（Grafana 负载测试 CLI；Windows amd64 MSI）", "可观测",
   "grafana/k6",
   installer_markers_match_all=True,
   installer_markers=["k6-v", "windows-amd64.msi"],
   href_exclude_substrings=_ex(".zip", "linux", "macos", "arm"),
   installer_extensions=[".msi"], windows_installer=True, run_installer=True,
   aliases=["k6", "grafana k6", "负载测试"])
_e("darwin", SH_OBS, "k6",
   "k6（Grafana 负载测试 CLI；macOS Apple Silicon zip）", "可观测",
   "grafana/k6",
   installer_markers_match_all=True,
   installer_markers=["k6-v", "macos-arm64.zip"],
   href_exclude_substrings=_ex("amd64", "linux", "windows"),
   installer_extensions=[".zip"],
   aliases=["k6", "grafana k6"])
_e("linux", SH_OBS, "k6",
   "k6（Grafana 负载测试 CLI；Debian amd64 deb）", "可观测",
   "grafana/k6",
   installer_markers_match_all=True,
   installer_markers=["k6-v", "linux-amd64.deb"],
   href_exclude_substrings=_ex("arm64", "rpm", "windows", "macos"),
   installer_extensions=[".deb"],
   aliases=["k6", "grafana k6"])

# --- 云原生：OpenTofu / Pulumi ---
_e("windows", SH_CN, "opentofu",
   "OpenTofu（Terraform 开源分支；Windows amd64 zip）", "云原生",
   "opentofu/opentofu",
   installer_markers_match_all=True,
   installer_markers=["tofu_", "windows_amd64.zip"],
   href_exclude_substrings=_ex(".sig", ".pem", ".gpgsig", "arm"),
   installer_extensions=[".zip"],
   aliases=["opentofu", "OpenTofu", "tofu", "terraform开源"])
_e("darwin", SH_CN, "opentofu",
   "OpenTofu（Terraform 开源分支；macOS Apple Silicon zip）", "云原生",
   "opentofu/opentofu",
   installer_markers_match_all=True,
   installer_markers=["tofu_", "darwin_arm64.zip"],
   href_exclude_substrings=_ex(".sig", ".pem", ".gpgsig", "amd64"),
   installer_extensions=[".zip"],
   aliases=["opentofu", "OpenTofu", "tofu"])
_e("linux", SH_CN, "opentofu",
   "OpenTofu（Terraform 开源分支；Linux amd64 zip）", "云原生",
   "opentofu/opentofu",
   installer_markers_match_all=True,
   installer_markers=["tofu_", "linux_amd64.zip"],
   href_exclude_substrings=_ex(".sig", ".pem", ".gpgsig", "arm", ".deb", ".rpm"),
   installer_extensions=[".zip"],
   aliases=["opentofu", "OpenTofu", "tofu"])
_e("windows", SH_CN, "pulumi",
   "Pulumi（现代 IaC CLI；Windows x64 zip）", "云原生",
   "pulumi/pulumi",
   installer_markers_match_all=True,
   installer_markers=["pulumi-v", "windows-x64.zip"],
   href_exclude_substrings=_ex(".sig", "arm64", "linux", "darwin"),
   installer_extensions=[".zip"],
   aliases=["pulumi", "Pulumi"])
_e("darwin", SH_CN, "pulumi",
   "Pulumi（现代 IaC CLI；macOS Apple Silicon tar.gz）", "云原生",
   "pulumi/pulumi",
   installer_markers_match_all=True,
   installer_markers=["pulumi-v", "darwin-arm64.tar.gz"],
   href_exclude_substrings=_ex(".sig", "x64", "linux", "windows"),
   installer_extensions=[".tar.gz"],
   aliases=["pulumi", "Pulumi"])
_e("linux", SH_CN, "pulumi",
   "Pulumi（现代 IaC CLI；Linux x64 tar.gz）", "云原生",
   "pulumi/pulumi",
   installer_markers_match_all=True,
   installer_markers=["pulumi-v", "linux-x64.tar.gz"],
   href_exclude_substrings=_ex(".sig", "arm64", "windows", "darwin"),
   installer_extensions=[".tar.gz"],
   aliases=["pulumi", "Pulumi"])

# --- 代理：Karing / GUI.for.Clash ---
_e("windows", SH_PROXY, "karing",
   "Karing（多协议代理客户端；Windows x64）", "代理与隧道",
   "KaringX/Karing",
   installer_markers_match_all=True,
   installer_markers=["karing_", "windows_x64.exe"],
   href_exclude_substrings=_ex(".zip", "android", "linux", "macos"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   process_name="karing.exe", kill_before_install=True,
   aliases=["karing", "Karing", "卡拉"] )
_e("darwin", SH_PROXY, "karing",
   "Karing（多协议代理客户端；macOS universal dmg）", "代理与隧道",
   "KaringX/Karing",
   installer_markers_match_all=True,
   installer_markers=["karing_", "macos_universal.dmg"],
   href_exclude_substrings=_ex(".pkg", "windows", "linux", "android"),
   installer_extensions=[".dmg"],
   aliases=["karing", "Karing"])
_e("linux", SH_PROXY, "karing",
   "Karing（多协议代理客户端；Debian amd64 deb）", "代理与隧道",
   "KaringX/Karing",
   installer_markers_match_all=True,
   installer_markers=["karing_", "linux_amd64.deb"],
   href_exclude_substrings=_ex("AppImage", "rpm", "windows", "android"),
   installer_extensions=[".deb"],
   aliases=["karing", "Karing"])
_e("windows", SH_PROXY, "gui_for_clash",
   "GUI.for.Clash（Clash/Mihomo 图形前端；Windows amd64 zip）", "代理与隧道",
   "GUI-for-Cores/GUI.for.Clash",
   installer_markers_match_all=True,
   installer_markers=["GUI.for.Clash-windows-amd64.zip"],
   href_exclude_substrings=_ex("arm64", "386", "linux", "darwin"),
   installer_extensions=[".zip"],
   aliases=["gui.for.clash", "GUI.for.Clash", "clash gui"])
_e("darwin", SH_PROXY, "gui_for_clash",
   "GUI.for.Clash（Clash/Mihomo 图形前端；macOS Apple Silicon zip）", "代理与隧道",
   "GUI-for-Cores/GUI.for.Clash",
   installer_markers_match_all=True,
   installer_markers=["GUI.for.Clash-darwin-arm64.zip"],
   href_exclude_substrings=_ex("amd64", "windows", "linux"),
   installer_extensions=[".zip"],
   aliases=["gui.for.clash", "GUI.for.Clash"])
_e("linux", SH_PROXY, "gui_for_clash",
   "GUI.for.Clash（Clash/Mihomo 图形前端；Linux amd64 zip）", "代理与隧道",
   "GUI-for-Cores/GUI.for.Clash",
   installer_markers_match_all=True,
   installer_markers=["GUI.for.Clash-linux-amd64.zip"],
   href_exclude_substrings=_ex("arm64", "windows", "darwin"),
   installer_extensions=[".zip"],
   aliases=["gui.for.clash", "GUI.for.Clash"])

# --- 局域网：OnionShare / sendme ---
_e("windows", SH_LAN, "onionshare",
   "OnionShare（Tor 匿名文件分享；Windows x64 MSI）", "局域网文件共享",
   "onionshare/onionshare",
   installer_markers_match_all=True,
   installer_markers=["OnionShare-win64-", ".msi"],
   href_exclude_substrings=_ex("dmg", "tar.gz"),
   installer_extensions=[".msi"], windows_installer=True, run_installer=True,
   process_name="onionshare.exe", kill_before_install=True,
   aliases=["onionshare", "OnionShare", "洋葱分享"])
_e("darwin", SH_LAN, "onionshare",
   "OnionShare（Tor 匿名文件分享；macOS dmg）", "局域网文件共享",
   "onionshare/onionshare",
   installer_markers_match_all=True,
   installer_markers=["OnionShare-", ".dmg"],
   href_exclude_substrings=_ex("win64", "tar.gz"),
   installer_extensions=[".dmg"],
   aliases=["onionshare", "OnionShare", "洋葱分享"])
_e("windows", SH_LAN, "sendme",
   "sendme（n0/iroh 点对点传文件 CLI；Windows x64 zip）", "局域网文件共享",
   "n0-computer/sendme",
   installer_markers_match_all=True,
   installer_markers=["sendme-v", "windows-x86_64.zip"],
   href_exclude_substrings=_ex("darwin", "linux", "aarch64"),
   installer_extensions=[".zip"],
   aliases=["sendme", "sendme iroh", "iroh sendme"])
_e("darwin", SH_LAN, "sendme",
   "sendme（n0/iroh 点对点传文件 CLI；macOS Apple Silicon tar.gz）", "局域网文件共享",
   "n0-computer/sendme",
   installer_markers_match_all=True,
   installer_markers=["sendme-v", "darwin-aarch64.tar.gz"],
   href_exclude_substrings=_ex("x86_64", "linux", "windows"),
   installer_extensions=[".tar.gz"],
   aliases=["sendme", "sendme iroh"])
_e("linux", SH_LAN, "sendme",
   "sendme（n0/iroh 点对点传文件 CLI；Linux x86_64 tar.gz）", "局域网文件共享",
   "n0-computer/sendme",
   installer_markers_match_all=True,
   installer_markers=["sendme-v", "linux-x86_64.tar.gz"],
   href_exclude_substrings=_ex("aarch64", "darwin", "windows"),
   installer_extensions=[".tar.gz"],
   aliases=["sendme", "sendme iroh"])

# --- 游戏：GDevelop ---
_e("windows", SH_GAME, "gdevelop",
   "GDevelop（无代码/低代码游戏引擎；Windows Setup）", "游戏",
   "4ian/GDevelop",
   installer_markers_match_all=True,
   installer_markers=["GDevelop-5-Setup-", ".exe"],
   href_exclude_substrings=_ex(".zip", "mac", "AppImage"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   process_name="GDevelop.exe", kill_before_install=True,
   aliases=["gdevelop", "GDevelop", "GDevelop 5"])
_e("darwin", SH_GAME, "gdevelop",
   "GDevelop（无代码/低代码游戏引擎；macOS universal dmg）", "游戏",
   "4ian/GDevelop",
   installer_markers_match_all=True,
   installer_markers=["GDevelop-5-", "-universal.dmg"],
   href_exclude_substrings=_ex(".zip", "Setup", "AppImage", "linux"),
   installer_extensions=[".dmg"],
   aliases=["gdevelop", "GDevelop"])
_e("linux", SH_GAME, "gdevelop",
   "GDevelop（无代码/低代码游戏引擎；Linux x64 AppImage）", "游戏",
   "4ian/GDevelop",
   installer_markers_match_all=True,
   installer_markers=["GDevelop-5-", ".AppImage"],
   href_exclude_substrings=_ex("arm64", "Setup", "windows", ".zip"),
   installer_extensions=[".AppImage"],
   aliases=["gdevelop", "GDevelop"])

# --- 终端：Wave Terminal ---
_e("windows", SH_TERM, "waveterm",
   "Wave Terminal（AI/工作区终端；Windows x64）", "终端",
   "wavetermdev/waveterm",
   installer_markers_match_all=True,
   installer_markers=["Wave-win32-x64-", ".exe"],
   href_exclude_substrings=_ex(".msi", ".zip", "darwin", "linux"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   process_name="Wave.exe", kill_before_install=True,
   aliases=["waveterm", "wave terminal", "Wave Terminal", "wave"])
_e("darwin", SH_TERM, "waveterm",
   "Wave Terminal（AI/工作区终端；macOS Apple Silicon dmg）", "终端",
   "wavetermdev/waveterm",
   installer_markers_match_all=True,
   installer_markers=["Wave-darwin-arm64-", ".dmg"],
   href_exclude_substrings=_ex(".zip", "x64", "windows", "linux"),
   installer_extensions=[".dmg"],
   aliases=["waveterm", "wave terminal", "Wave Terminal"])
_e("linux", SH_TERM, "waveterm",
   "Wave Terminal（AI/工作区终端；Debian amd64 deb）", "终端",
   "wavetermdev/waveterm",
   installer_markers_match_all=True,
   installer_markers=["waveterm-linux-amd64-", ".deb"],
   href_exclude_substrings=_ex("AppImage", "rpm", "arm64", "windows"),
   installer_extensions=[".deb"],
   aliases=["waveterm", "wave terminal", "Wave Terminal"])

# --- 开发：Yaak ---
_e("windows", SH_DEV, "yaak",
   "Yaak（本地优先 API 客户端；Windows x64 Setup）", "开发",
   "mountain-loop/yaak",
   installer_markers_match_all=True,
   installer_markers=["Yaak_", "_x64-setup.exe"],
   href_exclude_substrings=_ex("arm64", "machine", "linux", ".dmg"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   process_name="Yaak.exe", kill_before_install=True,
   aliases=["yaak", "Yaak", "yaak.app"])
_e("darwin", SH_DEV, "yaak",
   "Yaak（本地优先 API 客户端；macOS Apple Silicon dmg）", "开发",
   "mountain-loop/yaak",
   installer_markers_match_all=True,
   installer_markers=["Yaak_", "_aarch64.dmg"],
   href_exclude_substrings=_ex("x64", ".app.tar.gz", "windows", "linux"),
   installer_extensions=[".dmg"],
   aliases=["yaak", "Yaak"])
_e("linux", SH_DEV, "yaak",
   "Yaak（本地优先 API 客户端；Debian amd64 deb）", "开发",
   "mountain-loop/yaak",
   installer_markers_match_all=True,
   installer_markers=["yaak_", "_amd64.deb"],
   href_exclude_substrings=_ex("cef", "arm64", "AppImage", "windows"),
   installer_extensions=[".deb"],
   aliases=["yaak", "Yaak"])

# --- 效率：ActivityWatch（mac 最新仅 x86_64，darwin 跳过） ---
_e("windows", SH_EFF, "activitywatch",
   "ActivityWatch（开源自动时间追踪；Windows x64 Setup）", "效率",
   "ActivityWatch/activitywatch",
   installer_markers_match_all=True,
   installer_markers=["activitywatch-v", "windows-x86_64-setup.exe"],
   href_exclude_substrings=_ex(".zip", "linux", "macos"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   process_name="aw-qt.exe", kill_before_install=True,
   aliases=["activitywatch", "ActivityWatch", "时间追踪"])
_e("linux", SH_EFF, "activitywatch",
   "ActivityWatch（开源自动时间追踪；Debian x86_64 deb）", "效率",
   "ActivityWatch/activitywatch",
   installer_markers_match_all=True,
   installer_markers=["activitywatch-v", "linux-x86_64.deb"],
   href_exclude_substrings=_ex(".zip", "AppImage", "windows", "macos"),
   installer_extensions=[".deb"],
   aliases=["activitywatch", "ActivityWatch"])

# --- 网络：AdGuard Home ---
_e("windows", SH_NET, "adguardhome",
   "AdGuard Home（局域网 DNS 广告拦截；Windows amd64 zip）", "网络",
   "AdguardTeam/AdGuardHome",
   installer_markers_match_all=True,
   installer_markers=["AdGuardHome_windows_amd64.zip"],
   href_exclude_substrings=_ex("386", "arm64", "linux", "darwin"),
   installer_extensions=[".zip"],
   aliases=["adguardhome", "AdGuard Home", "adguard home", "广告拦截dns"])
_e("darwin", SH_NET, "adguardhome",
   "AdGuard Home（局域网 DNS 广告拦截；macOS Apple Silicon zip）", "网络",
   "AdguardTeam/AdGuardHome",
   installer_markers_match_all=True,
   installer_markers=["AdGuardHome_darwin_arm64.zip"],
   href_exclude_substrings=_ex("amd64", "linux", "windows"),
   installer_extensions=[".zip"],
   aliases=["adguardhome", "AdGuard Home"])
_e("linux", SH_NET, "adguardhome",
   "AdGuard Home（局域网 DNS 广告拦截；Linux amd64 tar.gz）", "网络",
   "AdguardTeam/AdGuardHome",
   installer_markers_match_all=True,
   installer_markers=["AdGuardHome_linux_amd64.tar.gz"],
   href_exclude_substrings=_ex("arm", "386", "frontend", "windows", "darwin"),
   installer_extensions=[".tar.gz"],
   aliases=["adguardhome", "AdGuard Home"])

# --- 通讯：SimpleX Desktop ---
_e("windows", SH_IM, "simplex_desktop",
   "SimpleX Chat 桌面（无用户 ID 的端到端加密聊天；Windows x64 MSI）", "网络与通讯",
   "simplex-chat/simplex-chat",
   installer_markers_match_all=True,
   installer_markers=["simplex-desktop-windows-x86_64.msi"],
   href_exclude_substrings=_ex("AppImage", "macos", "ubuntu", ".apk"),
   installer_extensions=[".msi"], windows_installer=True, run_installer=True,
   process_name="simplex-desktop.exe", kill_before_install=True,
   aliases=["simplex", "SimpleX", "simplex chat", "simplex桌面"])
_e("darwin", SH_IM, "simplex_desktop",
   "SimpleX Chat 桌面（无用户 ID 的端到端加密聊天；macOS Apple Silicon dmg）", "网络与通讯",
   "simplex-chat/simplex-chat",
   installer_markers_match_all=True,
   installer_markers=["simplex-desktop-macos-aarch64.dmg"],
   href_exclude_substrings=_ex("x86_64", "windows", "ubuntu", ".apk"),
   installer_extensions=[".dmg"],
   aliases=["simplex", "SimpleX", "simplex chat"])
_e("linux", SH_IM, "simplex_desktop",
   "SimpleX Chat 桌面（无用户 ID 的端到端加密聊天；Linux x86_64 AppImage）", "网络与通讯",
   "simplex-chat/simplex-chat",
   installer_markers_match_all=True,
   installer_markers=["simplex-desktop-x86_64.AppImage"],
   href_exclude_substrings=_ex("aarch64", "ubuntu", "windows", ".apk"),
   installer_extensions=[".AppImage"],
   aliases=["simplex", "SimpleX", "simplex chat"])

# --- Android：Karing APK ---
MOBILE_BATCH["30-代理与隧道.json"] = [{
    "id": "karing",
    "简介": "Karing（多协议代理客户端；Android arm64-v8a APK）",
    "分类": "代理与隧道",
    "aliases": ["karing", "Karing"],
    "enabled": False,
    "prefer_api_assets": True,
    "version_tag_as_on_github": True,
    "run_installer": False,
    "kill_before_install": False,
    "windows_installer": False,
    "process_name": "",
    "installer_extensions": [".apk"],
    "installer_markers_match_all": True,
    "installer_markers": ["karing_", "android_arm64-v8a.apk"],
    "href_exclude_substrings": [
        "armeabi", "android_arm.apk", "windows", "linux", "macos",
        "debug", ".aab", "unsigned", ".json", ".txt",
    ],
    "use_download_filename": True,
    "save_name": "karing.apk",
    "releases_url": "https://bgithub.xyz/KaringX/Karing/releases",
    "repo_path": "KaringX/Karing",
}]


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
            with open(path, encoding="utf-8", mode="w") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
            print(f"Wrote {path} ({len(data)} entries)")
    return added, skipped


def _merge_mobile(dry: bool) -> int:
    added = 0
    for shard, apps in sorted(MOBILE_BATCH.items()):
        path = os.path.join(MOBILE, "android", shard)
        existing = json.load(open(path, encoding="utf-8")) if os.path.isfile(path) else []
        seen = {(a.get("id") or "").strip() for a in existing if isinstance(a, dict)}
        for app in apps:
            aid = (app.get("id") or "").strip()
            if aid in seen:
                print(f"skip android/{aid}")
                continue
            existing.append(app)
            seen.add(aid)
            added += 1
        if not dry:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, encoding="utf-8", mode="w") as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)
                f.write("\n")
            print(f"Wrote {path} ({len(existing)} entries)")
    return added


def main():
    dry = "--dry-run" in sys.argv
    a, s = _merge_desktop(dry)
    m = _merge_mobile(dry)
    print(f"{'dry-run' if dry else 'done'}: desktop +{a} skip {s}; android +{m}")


if __name__ == "__main__":
    main()
