#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Batch26：与 SztuCode 同类的本地/桌面 AI 智能体、办公助手、本地 Chat、Agent 工作台。"""
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

# --- DeepChat：国产多模型桌面 Chat / Agent ---
_e("windows", SH_AI, "deepchat",
   "DeepChat（开源多模型 AI 桌面客户端；Windows x64）", "AI",
   "ThinkInAIXYZ/deepchat",
   installer_markers_match_all=True,
   installer_markers=["DeepChat-", "windows-x64.exe"],
   href_exclude_substrings=_ex("arm64", "linux", "mac", ".zip"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["deepchat", "DeepChat", "深度聊天"])
_e("darwin", SH_AI, "deepchat",
   "DeepChat（开源多模型 AI 桌面客户端；macOS Apple Silicon dmg）", "AI",
   "ThinkInAIXYZ/deepchat",
   installer_markers_match_all=True,
   installer_markers=["DeepChat-", "mac-arm64.dmg"],
   href_exclude_substrings=_ex("x64", "windows", "linux", ".zip"),
   installer_extensions=[".dmg"],
   aliases=["deepchat", "DeepChat"])
_e("linux", SH_AI, "deepchat",
   "DeepChat（开源多模型 AI 桌面客户端；Linux x86_64 AppImage）", "AI",
   "ThinkInAIXYZ/deepchat",
   installer_markers_match_all=True,
   installer_markers=["DeepChat-", "linux-x86_64.AppImage"],
   href_exclude_substrings=_ex("arm64", "windows", "mac", ".tar.gz", ".deb"),
   installer_extensions=[".AppImage"],
   aliases=["deepchat", "DeepChat"])

# --- 5ire：桌面 AI 助手 + MCP ---
_e("windows", SH_AI, "fiveire",
   "5ire（桌面 AI 助手 / MCP 客户端；Windows Setup）", "AI",
   "nanbingxyz/5ire",
   installer_markers_match_all=True,
   installer_markers=["5ire-Setup-", ".exe"],
   href_exclude_substrings=_ex("linux", "mac", ".zip"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["5ire", "fiveire", "fai-er"])
_e("darwin", SH_AI, "fiveire",
   "5ire（桌面 AI 助手 / MCP 客户端；macOS Apple Silicon dmg）", "AI",
   "nanbingxyz/5ire",
   installer_markers_match_all=True,
   installer_markers=["5ire-", "arm64.dmg"],
   href_exclude_substrings=_ex("windows", "linux", ".zip", "AppImage"),
   installer_extensions=[".dmg"],
   aliases=["5ire", "fiveire"])
_e("linux", SH_AI, "fiveire",
   "5ire（桌面 AI 助手 / MCP 客户端；Linux x86_64 AppImage）", "AI",
   "nanbingxyz/5ire",
   installer_markers_match_all=True,
   installer_markers=["5ire-", "x86_64.AppImage"],
   href_exclude_substrings=_ex("windows", "mac", ".dmg", ".exe"),
   installer_extensions=[".AppImage"],
   aliases=["5ire", "fiveire"])

# --- Witsy：桌面 AI 助手 / MCP ---
_e("windows", SH_AI, "witsy",
   "Witsy（桌面 AI 助手 / MCP 客户端；Windows x64 Setup）", "AI",
   "Kochava-Studios/witsy",
   installer_markers_match_all=True,
   installer_markers=["Witsy-", "win32-x64.Setup.exe"],
   href_exclude_substrings=_ex("arm64", "darwin", "linux", ".zip", ".nupkg"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["witsy", "Witsy", "nbonamy"])
_e("darwin", SH_AI, "witsy",
   "Witsy（桌面 AI 助手 / MCP 客户端；macOS Apple Silicon dmg）", "AI",
   "Kochava-Studios/witsy",
   installer_markers_match_all=True,
   installer_markers=["Witsy-", "darwin-arm64.dmg"],
   href_exclude_substrings=_ex("x64", "win32", "linux", ".zip"),
   installer_extensions=[".dmg"],
   aliases=["witsy", "Witsy"])
_e("linux", SH_AI, "witsy",
   "Witsy（桌面 AI 助手 / MCP 客户端；Linux amd64 deb）", "AI",
   "Kochava-Studios/witsy",
   installer_markers_match_all=True,
   installer_markers=["witsy_", "amd64.deb"],
   href_exclude_substrings=_ex("darwin", "win32", ".rpm", ".zip"),
   installer_extensions=[".deb"],
   aliases=["witsy", "Witsy"])

# --- Coco AI：本地搜索 + 助手 ---
_e("windows", SH_AI, "coco_ai",
   "Coco AI（本地搜索与个人助手桌面端；Windows x64 Setup）", "AI",
   "infinilabs/coco-app",
   installer_markers_match_all=True,
   installer_markers=["Coco-AI_", "x64-setup.exe"],
   href_exclude_substrings=_ex("arm64", "x86-setup", "linux", ".dmg"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["coco", "coco ai", "Coco AI", "infinilabs"])
_e("darwin", SH_AI, "coco_ai",
   "Coco AI（本地搜索与个人助手桌面端；macOS Apple Silicon dmg）", "AI",
   "infinilabs/coco-app",
   installer_markers_match_all=True,
   installer_markers=["Coco-AI_", "aarch64.dmg"],
   href_exclude_substrings=_ex("x64", "windows", "linux", ".exe"),
   installer_extensions=[".dmg"],
   aliases=["coco", "coco ai", "Coco AI"])
_e("linux", SH_AI, "coco_ai",
   "Coco AI（本地搜索与个人助手桌面端；Linux amd64 AppImage）", "AI",
   "infinilabs/coco-app",
   installer_markers_match_all=True,
   installer_markers=["Coco-AI_", "amd64.AppImage"],
   href_exclude_substrings=_ex("aarch64", "windows", ".dmg", ".deb", ".rpm"),
   installer_extensions=[".AppImage"],
   aliases=["coco", "coco ai", "Coco AI"])

# --- Dive AI Agent：MCP Host（与 wagoodman/dive 区分） ---
_e("windows", SH_AI, "dive_ai",
   "Dive AI Agent（开源 MCP Host 桌面智能体；Windows x64 Tauri Setup）", "AI",
   "OpenAgentPlatform/Dive",
   installer_markers_match_all=True,
   installer_markers=["dive_", "x64-setup.exe"],
   href_exclude_substrings=_ex("electron", "linux", "mac", ".msi"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["dive ai", "Dive AI", "openagentplatform"])
_e("darwin", SH_AI, "dive_ai",
   "Dive AI Agent（开源 MCP Host 桌面智能体；macOS Apple Silicon dmg）", "AI",
   "OpenAgentPlatform/Dive",
   installer_markers_match_all=True,
   installer_markers=["Dive-electron-", "mac-arm64.dmg"],
   href_exclude_substrings=_ex("x64", "windows", "linux", ".zip"),
   installer_extensions=[".dmg"],
   aliases=["dive ai", "Dive AI"])
_e("linux", SH_AI, "dive_ai",
   "Dive AI Agent（开源 MCP Host 桌面智能体；Linux x86_64 AppImage）", "AI",
   "OpenAgentPlatform/Dive",
   installer_markers_match_all=True,
   installer_markers=["Dive-electron-", "linux-x86_64.AppImage"],
   href_exclude_substrings=_ex("windows", "mac", ".deb", ".rpm", ".tar.gz"),
   installer_extensions=[".AppImage"],
   aliases=["dive ai", "Dive AI"])

# --- Noi：lencx 本地优先 AI 工作台 ---
_e("windows", SH_AI, "noi",
   "Noi（本地优先 AI 工作台 / 多会话桌面端；Windows Setup）", "AI",
   "lencx/Noi",
   installer_markers_match_all=True,
   installer_markers=["Noi-", "Setup.exe"],
   href_exclude_substrings=_ex(".msi", ".dmg", "AppImage", ".nupkg", "darwin"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["noi", "Noi", "lencx"])
_e("darwin", SH_AI, "noi",
   "Noi（本地优先 AI 工作台；macOS Apple Silicon dmg）", "AI",
   "lencx/Noi",
   installer_markers_match_all=True,
   installer_markers=["Noi-", "arm64.dmg"],
   href_exclude_substrings=_ex("x64", "windows", "linux", ".zip", ".exe"),
   installer_extensions=[".dmg"],
   aliases=["noi", "Noi"])
_e("linux", SH_AI, "noi",
   "Noi（本地优先 AI 工作台；Linux x64 AppImage）", "AI",
   "lencx/Noi",
   installer_markers_match_all=True,
   installer_markers=["Noi-", "x64.AppImage"],
   href_exclude_substrings=_ex("windows", "darwin", ".deb", ".rpm", ".dmg"),
   installer_extensions=[".AppImage"],
   aliases=["noi", "Noi"])

# --- LobsterAI：网易有道桌面办公 Agent（无 Linux 包） ---
_e("windows", SH_AI, "lobsterai",
   "LobsterAI（网易有道开源桌面办公智能体；Windows x64）", "AI",
   "netease-youdao/LobsterAI",
   installer_markers_match_all=True,
   installer_markers=["LobsterAI--", "win-x64.exe"],
   href_exclude_substrings=_ex("mac", ".dmg"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["lobsterai", "LobsterAI", "龙虾", "有道智能体"])
_e("darwin", SH_AI, "lobsterai",
   "LobsterAI（网易有道开源桌面办公智能体；macOS Apple Silicon dmg）", "AI",
   "netease-youdao/LobsterAI",
   installer_markers_match_all=True,
   installer_markers=["LobsterAI--", "mac-arm64.dmg"],
   href_exclude_substrings=_ex("x64", "win", ".exe"),
   installer_extensions=[".dmg"],
   aliases=["lobsterai", "LobsterAI", "龙虾"])

# --- Kun：本地优先 Agent 工作台 ---
_e("windows", SH_AI, "kun",
   "Kun（本地优先 AI Agent 工作台；Windows x64）", "AI",
   "KunAgent/Kun",
   installer_markers_match_all=True,
   installer_markers=["Kun-", "win-x64.exe"],
   href_exclude_substrings=_ex("linux", "mac", ".zip", ".dmg"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["kun", "Kun", "kun-agent", "KunAgent"])
_e("darwin", SH_AI, "kun",
   "Kun（本地优先 AI Agent 工作台；macOS Apple Silicon dmg）", "AI",
   "KunAgent/Kun",
   installer_markers_match_all=True,
   installer_markers=["Kun-", "mac-arm64.dmg"],
   href_exclude_substrings=_ex("x64", "windows", "linux", ".zip"),
   installer_extensions=[".dmg"],
   aliases=["kun", "Kun", "kun-agent"])
_e("linux", SH_AI, "kun",
   "Kun（本地优先 AI Agent 工作台；Linux x86_64 AppImage）", "AI",
   "KunAgent/Kun",
   installer_markers_match_all=True,
   installer_markers=["Kun-", "linux-x86_64.AppImage"],
   href_exclude_substrings=_ex("arm64", "windows", "mac", ".deb"),
   installer_extensions=[".AppImage"],
   aliases=["kun", "Kun", "kun-agent"])

# --- Deeting OS：本地优先工作台（latest 无 dmg，darwin 跳过） ---
_e("windows", SH_AI, "deeting",
   "Deeting OS（本地优先 AI 工作台；Windows x64 Setup）", "AI",
   "MarshallEriksen-Neura/Deeting",
   installer_markers_match_all=True,
   installer_markers=["deeting_", "x64-setup.exe"],
   href_exclude_substrings=_ex(".msi", "linux", ".dmg"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["deeting", "Deeting", "谛听"])
_e("linux", SH_AI, "deeting",
   "Deeting OS（本地优先 AI 工作台；Linux amd64 AppImage）", "AI",
   "MarshallEriksen-Neura/Deeting",
   installer_markers_match_all=True,
   installer_markers=["deeting_", "amd64.AppImage"],
   href_exclude_substrings=_ex("windows", ".deb", ".rpm", ".exe"),
   installer_extensions=[".AppImage"],
   aliases=["deeting", "Deeting", "谛听"])

# --- AxAgent：Tauri 桌面 Agent ---
_e("windows", SH_AI, "axagent",
   "AxAgent（Tauri 桌面 AI 智能体工作台；Windows x64 MSI）", "AI",
   "polite0803/AxAgent",
   installer_markers_match_all=True,
   installer_markers=["AxAgent_", "windows-x64.msi"],
   href_exclude_substrings=_ex("portable", "arm64", "linux", "macos"),
   installer_extensions=[".msi"], windows_installer=True, run_installer=True,
   aliases=["axagent", "AxAgent"])
_e("darwin", SH_AI, "axagent",
   "AxAgent（Tauri 桌面 AI 智能体工作台；macOS Apple Silicon dmg）", "AI",
   "polite0803/AxAgent",
   installer_markers_match_all=True,
   installer_markers=["AxAgent_", "macos-arm64.dmg"],
   href_exclude_substrings=_ex("x64", "windows", "linux"),
   installer_extensions=[".dmg"],
   aliases=["axagent", "AxAgent"])
_e("linux", SH_AI, "axagent",
   "AxAgent（Tauri 桌面 AI 智能体工作台；Linux x64 deb）", "AI",
   "polite0803/AxAgent",
   installer_markers_match_all=True,
   installer_markers=["AxAgent_", "linux-x64.deb"],
   href_exclude_substrings=_ex("arm64", "windows", "macos"),
   installer_extensions=[".deb"],
   aliases=["axagent", "AxAgent"])

# --- Nuphus：本地优先桌面 Agent ---
_e("windows", SH_AI, "nuphus",
   "Nuphus（本地优先桌面 AI 智能体；Windows x64 Setup）", "AI",
   "mrpulor-gh/nuphus",
   installer_markers_match_all=True,
   installer_markers=["nuphus-win32-x64-", "setup.exe"],
   href_exclude_substrings=_ex(".zip", "osx", "linux", ".dmg"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["nuphus", "Nuphus"])
_e("darwin", SH_AI, "nuphus",
   "Nuphus（本地优先桌面 AI 智能体；macOS Apple Silicon dmg）", "AI",
   "mrpulor-gh/nuphus",
   installer_markers_match_all=True,
   installer_markers=["nuphus-osx-arm64-", ".dmg"],
   href_exclude_substrings=_ex(".zip", "win32", "linux"),
   installer_extensions=[".dmg"],
   aliases=["nuphus", "Nuphus"])
_e("linux", SH_AI, "nuphus",
   "Nuphus（本地优先桌面 AI 智能体；Linux amd64 AppImage）", "AI",
   "mrpulor-gh/nuphus",
   installer_markers_match_all=True,
   installer_markers=["Nuphus_", "amd64.AppImage"],
   href_exclude_substrings=_ex(".deb", "windows", "osx", ".dmg"),
   installer_extensions=[".AppImage"],
   aliases=["nuphus", "Nuphus"])

# --- OpenHuman：本地优先个人 AI ---
_e("windows", SH_AI, "openhuman",
   "OpenHuman（开源本地优先个人 AI 桌面端；Windows x64 Setup）", "AI",
   "tinyhumansai/openhuman",
   installer_markers_match_all=True,
   installer_markers=["OpenHuman_", "x64-setup.exe"],
   href_exclude_substrings=_ex(".msi", "linux", ".dmg", "aarch64"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["openhuman", "OpenHuman"])
_e("darwin", SH_AI, "openhuman",
   "OpenHuman（开源本地优先个人 AI 桌面端；macOS Apple Silicon dmg）", "AI",
   "tinyhumansai/openhuman",
   installer_markers_match_all=True,
   installer_markers=["OpenHuman_", "aarch64.dmg"],
   href_exclude_substrings=_ex("x64", "windows", "linux", ".exe"),
   installer_extensions=[".dmg"],
   aliases=["openhuman", "OpenHuman"])
_e("linux", SH_AI, "openhuman",
   "OpenHuman（开源本地优先个人 AI 桌面端；Linux amd64 AppImage）", "AI",
   "tinyhumansai/openhuman",
   installer_markers_match_all=True,
   installer_markers=["OpenHuman_", "amd64.AppImage"],
   href_exclude_substrings=_ex("aarch64", "windows", ".dmg", ".deb"),
   installer_extensions=[".AppImage"],
   aliases=["openhuman", "OpenHuman"])

# --- LiveAgent：桌面 Agent 客户端 ---
_e("windows", SH_AI, "live_agent",
   "LiveAgent（开源 AI Agent 桌面客户端；Windows x64 Setup）", "AI",
   "Stack-Cairn/LiveAgent",
   installer_markers_match_all=True,
   installer_markers=["LiveAgent-", "Windows-x64-Setup.exe"],
   href_exclude_substrings=_ex(".msi", "portable", "linux", "macOS"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["liveagent", "live agent", "LiveAgent", "stack-cairn"])
_e("darwin", SH_AI, "live_agent",
   "LiveAgent（开源 AI Agent 桌面客户端；macOS Apple Silicon dmg）", "AI",
   "Stack-Cairn/LiveAgent",
   installer_markers_match_all=True,
   installer_markers=["LiveAgent-", "macOS-aarch64.dmg"],
   href_exclude_substrings=_ex("x64", "Windows", "Linux", ".tar.gz"),
   installer_extensions=[".dmg"],
   aliases=["liveagent", "live agent", "LiveAgent"])
_e("linux", SH_AI, "live_agent",
   "LiveAgent（开源 AI Agent 桌面客户端；Linux x86_64 AppImage）", "AI",
   "Stack-Cairn/LiveAgent",
   installer_markers_match_all=True,
   installer_markers=["LiveAgent-", "Linux-x86_64.AppImage"],
   href_exclude_substrings=_ex("Windows", "macOS", ".deb", ".rpm"),
   installer_extensions=[".AppImage"],
   aliases=["liveagent", "live agent", "LiveAgent"])

# --- Flock：Tauri 多 Agent 工作台 ---
_e("windows", SH_AI, "flock",
   "Flock（Tauri 桌面多 Agent 工作台；Windows x64 Setup）", "AI",
   "Onelevenvy/flock",
   installer_markers_match_all=True,
   installer_markers=["Flock_", "x64-setup.exe"],
   href_exclude_substrings=_ex(".msi", "linux", ".dmg"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["flock", "Flock", "onelevenvy"])
_e("darwin", SH_AI, "flock",
   "Flock（Tauri 桌面多 Agent 工作台；macOS universal dmg）", "AI",
   "Onelevenvy/flock",
   installer_markers_match_all=True,
   installer_markers=["Flock_", "universal.dmg"],
   href_exclude_substrings=_ex("windows", "linux", ".exe"),
   installer_extensions=[".dmg"],
   aliases=["flock", "Flock"])
_e("linux", SH_AI, "flock",
   "Flock（Tauri 桌面多 Agent 工作台；Linux amd64 AppImage）", "AI",
   "Onelevenvy/flock",
   installer_markers_match_all=True,
   installer_markers=["Flock_", "amd64.AppImage"],
   href_exclude_substrings=_ex(".deb", ".rpm", "windows", ".dmg"),
   installer_extensions=[".AppImage"],
   aliases=["flock", "Flock"])

# --- Open Science Desktop：本地优先科研工作台 ---
_e("windows", SH_AI, "open_science",
   "Open Science Desktop（本地优先科研 AI 工作台；Windows x64 Setup）", "AI",
   "ai4s-research/open-science",
   installer_markers_match_all=True,
   installer_markers=["Open.Science_", "x64-setup.exe"],
   href_exclude_substrings=_ex(".msi", "linux", ".dmg"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["open science", "Open Science", "osd"])
_e("darwin", SH_AI, "open_science",
   "Open Science Desktop（本地优先科研 AI 工作台；macOS Apple Silicon dmg）", "AI",
   "ai4s-research/open-science",
   installer_markers_match_all=True,
   installer_markers=["Open.Science_", "aarch64.dmg"],
   href_exclude_substrings=_ex("x64", "windows", "linux", ".exe"),
   installer_extensions=[".dmg"],
   aliases=["open science", "Open Science", "osd"])
_e("linux", SH_AI, "open_science",
   "Open Science Desktop（本地优先科研 AI 工作台；Linux amd64 deb）", "AI",
   "ai4s-research/open-science",
   installer_markers_match_all=True,
   installer_markers=["Open.Science_", "amd64.deb"],
   href_exclude_substrings=_ex(".rpm", "windows", ".dmg", ".exe"),
   installer_extensions=[".deb"],
   aliases=["open science", "Open Science", "osd"])

# --- Jaz：Enchanted 后继，Ollama 原生 Chat（无 Linux 桌面包） ---
_e("windows", SH_AI, "jaz",
   "Jaz（Ollama 原生本地 Chat 桌面端；Windows Setup）", "AI",
   "gluonfield/jaz",
   installer_markers_match_all=True,
   installer_markers=["Jaz.Setup.", ".exe"],
   href_exclude_substrings=_ex(".zip", "mac", "linux", "backend"),
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["jaz", "Jaz", "enchanted"])
_e("darwin", SH_AI, "jaz",
   "Jaz（Ollama 原生本地 Chat 桌面端；macOS Apple Silicon dmg）", "AI",
   "gluonfield/jaz",
   installer_markers_match_all=True,
   installer_markers=["Jaz-", "arm64.dmg"],
   href_exclude_substrings=_ex(".zip", "windows", "linux", "backend"),
   installer_extensions=[".dmg"],
   aliases=["jaz", "Jaz", "enchanted"])


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
            with open(path, encoding="utf-8", mode="w") as f:
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
