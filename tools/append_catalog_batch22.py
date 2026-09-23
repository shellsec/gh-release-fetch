#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Batch22：GitHub 近期热门且有 Release 二进制、尚未入库。"""
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


SH_AI = "01-AI.json"
SH_SYS = "16-系统.json"
SH_DEV = "12-开发.json"
SH_ED = "26-编辑器.json"
SH_AV = "22-音视频.json"
SH_EF = "13-效率.json"
SH_TERM = "17-终端.json"

# --- OpenLogi：罗技 Options+ 开源替代 ---
_e("windows", SH_SYS, "openlogi",
   "OpenLogi（罗技 Options+ 本地开源替代；Windows x64 MSI）", "系统",
   "AprilNEA/OpenLogi",
   installer_markers_match_all=True,
   installer_markers=["OpenLogi-v", "windows-x86_64.msi"],
   href_exclude_substrings=["arm64", ".zip", ".minisig", "linux", "macos"],
   installer_extensions=[".msi"], windows_installer=True, run_installer=True,
   aliases=["openlogi", "logitech options", "罗技", "Options+"])
_e("darwin", SH_SYS, "openlogi",
   "OpenLogi（macOS Apple Silicon dmg）", "系统",
   "AprilNEA/OpenLogi",
   installer_markers_match_all=True,
   installer_markers=["OpenLogi-v", "macos-arm64.dmg"],
   href_exclude_substrings=["x86_64", "windows", "linux", ".minisig"],
   installer_extensions=[".dmg"],
   aliases=["openlogi", "logitech options", "罗技", "Options+"])
_e("linux", SH_SYS, "openlogi",
   "OpenLogi（Linux amd64 deb）", "系统",
   "AprilNEA/OpenLogi",
   installer_markers_match_all=True,
   installer_markers=["openlogi-v", "linux-amd64.deb"],
   href_exclude_substrings=["arm64", ".rpm", "windows", "macos", ".minisig"],
   installer_extensions=[".deb"],
   aliases=["openlogi", "logitech options", "罗技", "Options+"])

# --- Colibri：本地 MoE 推理 ---
_e("windows", SH_AI, "colibri",
   "Colibri（本地跑前沿 MoE；Windows x64 zip）", "AI",
   "JustVugg/colibri",
   installer_markers_match_all=True,
   installer_markers=["colibri-v", "windows-x86_64.zip"],
   href_exclude_substrings=["linux", "macos", "darwin", "arm64"],
   installer_extensions=[".zip"],
   aliases=["colibri", "Colibri"])
_e("darwin", SH_AI, "colibri",
   "Colibri（macOS Apple Silicon tar.gz）", "AI",
   "JustVugg/colibri",
   installer_markers_match_all=True,
   installer_markers=["colibri-v", "macos-arm64.tar.gz"],
   href_exclude_substrings=["linux", "windows", "x86_64"],
   installer_extensions=[".tar.gz"],
   aliases=["colibri", "Colibri"])
_e("linux", SH_AI, "colibri",
   "Colibri（Linux x86_64 tar.gz）", "AI",
   "JustVugg/colibri",
   installer_markers_match_all=True,
   installer_markers=["colibri-v", "linux-x86_64.tar.gz"],
   href_exclude_substrings=["windows", "macos", "darwin", "arm64"],
   installer_extensions=[".tar.gz"],
   aliases=["colibri", "Colibri"])

# --- DSH Desktop ---
_e("windows", SH_AI, "dsh_desktop",
   "DSH Desktop（DeepSeek Harness 桌面端；Windows x64 Setup）", "AI",
   "anywhere-labs/dsh-desktop",
   installer_markers_match_all=True,
   installer_markers=["DSH-Desktop-", "x64-Setup.exe"],
   href_exclude_substrings=[".dmg", ".zip", "arm64", "linux"],
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["dsh", "dsh desktop", "DeepSeek Harness", "deepseek harness"])
_e("darwin", SH_AI, "dsh_desktop",
   "DSH Desktop（macOS universal dmg）", "AI",
   "anywhere-labs/dsh-desktop",
   installer_markers_match_all=True,
   installer_markers=["DSH.Desktop-", "universal.dmg"],
   href_exclude_substrings=[".exe", ".zip", "linux"],
   installer_extensions=[".dmg"],
   aliases=["dsh", "dsh desktop", "DeepSeek Harness", "deepseek harness"])

# --- OpenWorker ---
_e("windows", SH_AI, "openworker",
   "OpenWorker（Andrew Ng 开源 agent 工作台；Windows x64 Setup）", "AI",
   "andrewyng/openworker",
   installer_markers_match_all=True,
   installer_markers=["OpenWorker_", "x64-setup.exe"],
   href_exclude_substrings=[".msi", ".dmg", ".zip", "linux", "macos"],
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["openworker", "OpenWorker", "andrew ng"])
_e("darwin", SH_AI, "openworker",
   "OpenWorker（macOS Apple Silicon dmg）", "AI",
   "andrewyng/openworker",
   installer_markers_match_all=True,
   installer_markers=["OpenWorker_", "aarch64.dmg"],
   href_exclude_substrings=["x64", "windows", ".exe", ".msi"],
   installer_extensions=[".dmg"],
   aliases=["openworker", "OpenWorker", "andrew ng"])

# --- MiMo Code ---
_e("windows", SH_AI, "mimo_code",
   "MiMo Code（小米 MiMo 编码 CLI；Windows x64 zip）", "AI",
   "XiaomiMiMo/MiMo-Code",
   installer_markers_match_all=True,
   installer_markers=["mimocode-windows-x64.zip"],
   href_exclude_substrings=["baseline", "arm64", "darwin", "linux"],
   installer_extensions=[".zip"],
   aliases=["mimocode", "mimo code", "MiMo", "小米代码"])
_e("darwin", SH_AI, "mimo_code",
   "MiMo Code（macOS Apple Silicon zip）", "AI",
   "XiaomiMiMo/MiMo-Code",
   installer_markers_match_all=True,
   installer_markers=["mimocode-darwin-arm64.zip"],
   href_exclude_substrings=["x64", "windows", "linux", "baseline"],
   installer_extensions=[".zip"],
   aliases=["mimocode", "mimo code", "MiMo", "小米代码"])
_e("linux", SH_AI, "mimo_code",
   "MiMo Code（Linux x64 tar.gz）", "AI",
   "XiaomiMiMo/MiMo-Code",
   installer_markers_match_all=True,
   installer_markers=["mimocode-linux-x64.tar.gz"],
   href_exclude_substrings=["musl", "baseline", "arm64", "windows", "darwin"],
   installer_extensions=[".tar.gz"],
   aliases=["mimocode", "mimo code", "MiMo", "小米代码"])

# --- FreeLLMAPI ---
_e("windows", SH_AI, "freellmapi",
   "FreeLLMAPI（聚合免费 LLM 接口的桌面端；Windows Setup）", "AI",
   "tashfeenahmed/freellmapi",
   installer_markers_match_all=True,
   installer_markers=["FreeLLMAPI.Setup.", ".exe"],
   href_exclude_substrings=[".zip", ".blockmap", ".dmg", "AppImage", "linux"],
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["freellmapi", "free llm api", "FreeLLMAPI"])
_e("darwin", SH_AI, "freellmapi",
   "FreeLLMAPI（macOS Apple Silicon dmg）", "AI",
   "tashfeenahmed/freellmapi",
   installer_markers_match_all=True,
   installer_markers=["FreeLLMAPI-", "arm64.dmg"],
   href_exclude_substrings=[".blockmap", ".exe", "AppImage", "win"],
   installer_extensions=[".dmg"],
   aliases=["freellmapi", "free llm api", "FreeLLMAPI"])
_e("linux", SH_AI, "freellmapi",
   "FreeLLMAPI（Linux AppImage）", "AI",
   "tashfeenahmed/freellmapi",
   installer_markers_match_all=True,
   installer_markers=["FreeLLMAPI-", ".AppImage"],
   href_exclude_substrings=[".deb", ".exe", ".dmg", ".zip"],
   installer_extensions=[".AppImage"],
   aliases=["freellmapi", "free llm api", "FreeLLMAPI"])

# --- OpenClaw Manager ---
_e("windows", SH_AI, "openclaw_manager",
   "OpenClaw Manager（OpenClaw 桌面管理器；Windows x64 Setup）", "AI",
   "miaoxworld/openclaw-manager",
   installer_markers_match_all=True,
   installer_markers=["OpenClaw.Manager_", "x64-setup.exe"],
   href_exclude_substrings=[".msi", ".dmg", "AppImage", ".deb", "arm64"],
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["openclaw manager", "虾池子", "openclaw-manager"])
_e("darwin", SH_AI, "openclaw_manager",
   "OpenClaw Manager（macOS universal dmg）", "AI",
   "miaoxworld/openclaw-manager",
   installer_markers_match_all=True,
   installer_markers=["OpenClaw.Manager_", "universal.dmg"],
   href_exclude_substrings=[".exe", "AppImage", ".deb", ".msi"],
   installer_extensions=[".dmg"],
   aliases=["openclaw manager", "虾池子", "openclaw-manager"])
_e("linux", SH_AI, "openclaw_manager",
   "OpenClaw Manager（Linux amd64 AppImage）", "AI",
   "miaoxworld/openclaw-manager",
   installer_markers_match_all=True,
   installer_markers=["OpenClaw.Manager_", "amd64.AppImage"],
   href_exclude_substrings=["aarch64", ".deb", ".exe", ".dmg"],
   installer_extensions=[".AppImage"],
   aliases=["openclaw manager", "虾池子", "openclaw-manager"])

# --- agent-manager ---
_e("darwin", SH_TERM, "agent_manager",
   "agent-manager（tmux 里并行管多个编码 Agent；macOS arm64 tar.gz）", "终端",
   "yoanwai/agent-manager",
   installer_markers_match_all=True,
   installer_markers=["agent-manager_", "darwin_arm64.tar.gz"],
   href_exclude_substrings=["linux", "amd64", "checksum"],
   installer_extensions=[".tar.gz"],
   aliases=["agent-manager", "agent manager"])
_e("linux", SH_TERM, "agent_manager",
   "agent-manager（Linux amd64 tar.gz；Windows 请用 WSL）", "终端",
   "yoanwai/agent-manager",
   installer_markers_match_all=True,
   installer_markers=["agent-manager_", "linux_amd64.tar.gz"],
   href_exclude_substrings=["darwin", "arm64", "checksum"],
   installer_extensions=[".tar.gz"],
   aliases=["agent-manager", "agent manager"])

# --- T3 Code ---
_e("windows", SH_ED, "t3code",
   "T3 Code（Ping.gg 开源 AI 编辑器；Windows x64）", "编辑器",
   "pingdotgg/t3code",
   installer_markers_match_all=True,
   installer_markers=["T3-Code-", "x64.exe"],
   href_exclude_substrings=[".zip", ".blockmap", ".dmg", "AppImage", "arm64"],
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["t3code", "t3 code", "T3 Code"])
_e("darwin", SH_ED, "t3code",
   "T3 Code（macOS Apple Silicon dmg）", "编辑器",
   "pingdotgg/t3code",
   installer_markers_match_all=True,
   installer_markers=["T3-Code-", "arm64.dmg"],
   href_exclude_substrings=[".zip", ".blockmap", ".exe", "AppImage", "x64"],
   installer_extensions=[".dmg"],
   aliases=["t3code", "t3 code", "T3 Code"])
_e("linux", SH_ED, "t3code",
   "T3 Code（Linux x86_64 AppImage）", "编辑器",
   "pingdotgg/t3code",
   installer_markers_match_all=True,
   installer_markers=["T3-Code-", "x86_64.AppImage"],
   href_exclude_substrings=[".exe", ".dmg", ".zip"],
   installer_extensions=[".AppImage"],
   aliases=["t3code", "t3 code", "T3 Code"])

# --- GitDesktop / GitCat ---
_e("windows", SH_DEV, "gitdesktop",
   "GitDesktop（AI 原生 Git 桌面客户端；Windows x64 Setup）", "开发",
   "theBGuy/GitDesktop",
   installer_markers_match_all=True,
   installer_markers=["GitDesktop_", "x64-setup.exe"],
   href_exclude_substrings=[".msi", ".sig", ".dmg", "AppImage", ".deb"],
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["gitdesktop", "GitDesktop", "git desktop"])
_e("darwin", SH_DEV, "gitdesktop",
   "GitDesktop（macOS universal dmg）", "开发",
   "theBGuy/GitDesktop",
   installer_markers_match_all=True,
   installer_markers=["GitDesktop_", "universal.dmg"],
   href_exclude_substrings=[".exe", "AppImage", ".deb", ".sig", ".msi"],
   installer_extensions=[".dmg"],
   aliases=["gitdesktop", "GitDesktop", "git desktop"])
_e("linux", SH_DEV, "gitdesktop",
   "GitDesktop（Linux amd64 AppImage）", "开发",
   "theBGuy/GitDesktop",
   installer_markers_match_all=True,
   installer_markers=["GitDesktop_", "amd64.AppImage"],
   href_exclude_substrings=[".deb", ".rpm", ".exe", ".dmg", ".sig"],
   installer_extensions=[".AppImage"],
   aliases=["gitdesktop", "GitDesktop", "git desktop"])

_e("windows", SH_DEV, "gitcat",
   "GitCat（可撤销操作的 Git 客户端；Windows x64 Setup）", "开发",
   "zangjiucheng/GitCat",
   installer_markers_match_all=True,
   installer_markers=["GitCat_", "x64-setup.exe"],
   href_exclude_substrings=[".msi", ".sig", ".dmg", "AppImage", "arm64"],
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["gitcat", "GitCat"])
_e("darwin", SH_DEV, "gitcat",
   "GitCat（macOS Apple Silicon dmg）", "开发",
   "zangjiucheng/GitCat",
   installer_markers_match_all=True,
   installer_markers=["GitCat_", "aarch64.dmg"],
   href_exclude_substrings=["x64", ".exe", "AppImage", ".sig", ".msi"],
   installer_extensions=[".dmg"],
   aliases=["gitcat", "GitCat"])
_e("linux", SH_DEV, "gitcat",
   "GitCat（Linux amd64 AppImage）", "开发",
   "zangjiucheng/GitCat",
   installer_markers_match_all=True,
   installer_markers=["GitCat_", "amd64.AppImage"],
   href_exclude_substrings=["aarch64", ".deb", ".rpm", ".exe", ".dmg", ".sig"],
   installer_extensions=[".AppImage"],
   aliases=["gitcat", "GitCat"])

# --- 阿里 Open Code Review（仅 Windows 有 exe）---
_e("windows", SH_DEV, "open_code_review",
   "Open Code Review（阿里开源代码评审 CLI；Windows amd64 exe）", "开发",
   "alibaba/open-code-review",
   installer_markers_match_all=True,
   installer_markers=["opencodereview-windows-amd64.exe"],
   href_exclude_substrings=["arm64"],
   installer_extensions=[".exe"],
   aliases=["opencodereview", "open code review", "阿里代码评审"])

# --- Microsoft Edit ---
_e("windows", SH_ED, "microsoft_edit",
   "Microsoft Edit（微软终端编辑器；Windows x64 zip）", "编辑器",
   "microsoft/edit",
   installer_markers_match_all=True,
   installer_markers=["edit-", "x86_64-windows.zip"],
   href_exclude_substrings=["aarch64", "linux", "darwin", "apple"],
   installer_extensions=[".zip"],
   aliases=["msedit", "microsoft edit", "edit.exe", "微软edit"])
_e("darwin", SH_ED, "microsoft_edit",
   "Microsoft Edit（macOS Apple Silicon tar.gz）", "编辑器",
   "microsoft/edit",
   installer_markers_match_all=True,
   installer_markers=["edit-", "aarch64-apple-darwin.tar.gz"],
   href_exclude_substrings=["windows", "linux", "x86_64"],
   installer_extensions=[".tar.gz"],
   aliases=["msedit", "microsoft edit", "微软edit"])
_e("linux", SH_ED, "microsoft_edit",
   "Microsoft Edit（Linux x86_64 tar.gz）", "编辑器",
   "microsoft/edit",
   installer_markers_match_all=True,
   installer_markers=["edit-", "x86_64-linux-gnu.tar.gz"],
   href_exclude_substrings=["aarch64", "windows", "darwin", "apple"],
   installer_extensions=[".tar.gz"],
   aliases=["msedit", "microsoft edit", "微软edit"])

# --- Codex Dream Skin ---
_e("windows", SH_AI, "codex_dream_skin",
   "Codex Dream Skin（Codex 桌面美化/皮肤；Windows Setup）", "AI",
   "Fei-Away/Codex-Dream-Skin",
   installer_markers_match_all=True,
   installer_markers=["CodexDreamSkin-Setup-", ".exe"],
   href_exclude_substrings=[".dmg", ".zip"],
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["codex dream skin", "CodexDreamSkin"])
_e("darwin", SH_AI, "codex_dream_skin",
   "Codex Dream Skin（macOS dmg）", "AI",
   "Fei-Away/Codex-Dream-Skin",
   installer_markers_match_all=True,
   installer_markers=["CodexDreamSkin-", ".dmg"],
   href_exclude_substrings=[".exe", "Setup"],
   installer_extensions=[".dmg"],
   aliases=["codex dream skin", "CodexDreamSkin"])

# --- Mineradio ---
_e("windows", SH_AV, "mineradio",
   "Mineradio（沉浸式歌词/粒子音乐播放器；Windows Setup）", "音视频",
   "XxHuberrr/Mineradio",
   installer_markers_match_all=True,
   installer_markers=["Mineradio-", "Setup.exe"],
   href_exclude_substrings=[".zip", ".dmg"],
   installer_extensions=[".exe"], windows_installer=True, run_installer=True,
   aliases=["mineradio", "Mineradio"])

# --- Vorssaint Utils（仅 macOS）---
_e("darwin", SH_EF, "vorssaint",
   "Vorssaint Utils（开源 macOS 菜单栏工具箱）", "效率",
   "vorssaintapp/vorssaint-utils",
   installer_markers_match_all=True,
   installer_markers=["Vorssaint-", ".dmg"],
   href_exclude_substrings=[".zip", ".exe"],
   installer_extensions=[".dmg"],
   aliases=["vorssaint", "Vorssaint"])


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
