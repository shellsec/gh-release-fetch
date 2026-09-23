#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Batch16：对话待加（Terax / Reasonix）+ 扫描补缺（Clash Party / v2rayA / jj）+ UniGetUI/Hiddify 路径修正。"""
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
            ".minisig",
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


def _entry(plat: str, shard: str, aid: str, 简介: str, 分类: str, repo: str, **cfg):
    _add(
        plat,
        shard,
        [{"id": aid, "简介": 简介, "分类": 分类, **_b(**cfg), **_repo(repo)}],
    )


# --- Terax AI（桌面工作区）→ 编辑器 ---
_entry(
    "windows",
    "26-编辑器.json",
    "terax_ai",
    "Terax（轻量终端优先 AI 开发工作区；Windows x64 Setup）",
    "编辑器",
    "crynta/terax-ai",
    installer_markers_match_all=True,
    installer_markers=["Terax_", "x64-setup.exe"],
    href_exclude_substrings=[".msi", ".sig", "arm64", "ia32"],
    installer_extensions=[".exe"],
    windows_installer=True,
    run_installer=True,
    process_name="Terax.exe",
    kill_before_install=True,
)
_entry(
    "darwin",
    "26-编辑器.json",
    "terax_ai",
    "Terax（轻量终端优先 AI 开发工作区；macOS Apple Silicon dmg）",
    "编辑器",
    "crynta/terax-ai",
    installer_markers_match_all=True,
    installer_markers=["Terax_", "aarch64.dmg"],
    href_exclude_substrings=[".sig", "x64.dmg", "app.tar.gz"],
    installer_extensions=[".dmg"],
)
_entry(
    "linux",
    "26-编辑器.json",
    "terax_ai",
    "Terax（轻量终端优先 AI 开发工作区；Linux amd64 AppImage）",
    "编辑器",
    "crynta/terax-ai",
    installer_markers_match_all=True,
    installer_markers=["Terax_", "amd64.AppImage"],
    href_exclude_substrings=[".sig", ".deb", ".rpm"],
    installer_extensions=[".AppImage"],
)

# --- DeepSeek Reasonix Desktop → AI ---
_entry(
    "windows",
    "01-AI.json",
    "deepseek_reasonix",
    "DeepSeek Reasonix（DeepSeek 原生终端 AI coding agent / Desktop；Windows x64 安装包）",
    "AI",
    "esengine/DeepSeek-Reasonix",
    installer_markers_match_all=True,
    installer_markers=["Reasonix-windows-amd64-installer", ".exe"],
    href_exclude_substrings=["arm64", ".zip", ".minisig"],
    installer_extensions=[".exe"],
    windows_installer=True,
    run_installer=True,
)
_entry(
    "darwin",
    "01-AI.json",
    "deepseek_reasonix",
    "DeepSeek Reasonix Desktop（macOS universal dmg）",
    "AI",
    "esengine/DeepSeek-Reasonix",
    installer_markers_match_all=True,
    installer_markers=["Reasonix-darwin-universal", ".dmg"],
    href_exclude_substrings=[".zip", ".minisig"],
    installer_extensions=[".dmg"],
)
_entry(
    "linux",
    "01-AI.json",
    "deepseek_reasonix",
    "DeepSeek Reasonix Desktop（Linux amd64 deb）",
    "AI",
    "esengine/DeepSeek-Reasonix",
    installer_markers_match_all=True,
    installer_markers=["Reasonix-linux-amd64", ".deb"],
    href_exclude_substrings=[".tar.gz", ".minisig"],
    installer_extensions=[".deb"],
)

# --- Clash Party（原 Mihomo Party）→ 代理 ---
_entry(
    "windows",
    "30-代理与隧道.json",
    "clash_party",
    "Clash Party（原 Mihomo Party；Windows x64 Setup）",
    "代理与隧道",
    "mihomo-party-org/clash-party",
    installer_markers_match_all=True,
    installer_markers=["clash-party-windows-", "x64-setup.exe"],
    href_exclude_substrings=["win7", "ia32", "arm64", "mihomo-party", "portable", ".zip"],
    installer_extensions=[".exe"],
    windows_installer=True,
    run_installer=True,
)
_entry(
    "darwin",
    "30-代理与隧道.json",
    "clash_party",
    "Clash Party（原 Mihomo Party；macOS Apple Silicon pkg）",
    "代理与隧道",
    "mihomo-party-org/clash-party",
    installer_markers_match_all=True,
    installer_markers=["clash-party-macos-", "arm64.pkg"],
    href_exclude_substrings=["catalina", "x64", "mihomo-party", ".dmg", ".zip"],
    installer_extensions=[".pkg"],
)
_entry(
    "linux",
    "30-代理与隧道.json",
    "clash_party",
    "Clash Party（原 Mihomo Party；Linux amd64 deb）",
    "代理与隧道",
    "mihomo-party-org/clash-party",
    installer_markers_match_all=True,
    installer_markers=["clash-party-linux-", "amd64.deb"],
    href_exclude_substrings=["arm64", "rpm", "mihomo-party", "AppImage"],
    installer_extensions=[".deb"],
)

# --- v2rayA ---
_entry(
    "windows",
    "30-代理与隧道.json",
    "v2raya",
    "v2rayA（Web UI 管理的代理客户端；Windows x64 Inno 安装包）",
    "代理与隧道",
    "v2rayA/v2rayA",
    installer_markers_match_all=True,
    installer_markers=["installer_windows_inno_x64_", ".exe"],
    href_exclude_substrings=["arm64", "v2raya_core", "v2raya_windows", ".zip"],
    installer_extensions=[".exe"],
    windows_installer=True,
    run_installer=True,
)
_entry(
    "linux",
    "30-代理与隧道.json",
    "v2raya",
    "v2rayA（Web UI 管理的代理客户端；Debian amd64 deb）",
    "代理与隧道",
    "v2rayA/v2rayA",
    installer_markers_match_all=True,
    installer_markers=["installer_debian_x64_", ".deb"],
    href_exclude_substrings=["arm", "mips", "riscv", "loong", "redhat", "windows"],
    installer_extensions=[".deb"],
)

# --- jj (Jujutsu) → 开发 ---
_entry(
    "windows",
    "12-开发.json",
    "jj",
    "jj / Jujutsu（下一代 Git 兼容版本控制 CLI；Windows x64 zip）",
    "开发",
    "jj-vcs/jj",
    installer_markers_match_all=True,
    installer_markers=["jj-v", "x86_64-pc-windows-msvc.zip"],
    href_exclude_substrings=["aarch64", "docs", "linux", "darwin", "apple"],
    installer_extensions=[".zip"],
)
_entry(
    "darwin",
    "12-开发.json",
    "jj",
    "jj / Jujutsu（macOS Apple Silicon tar.gz）",
    "开发",
    "jj-vcs/jj",
    installer_markers_match_all=True,
    installer_markers=["jj-v", "aarch64-apple-darwin.tar.gz"],
    href_exclude_substrings=["x86_64", "docs", "linux", "windows"],
    installer_extensions=[".tar.gz"],
)
_entry(
    "linux",
    "12-开发.json",
    "jj",
    "jj / Jujutsu（Linux x86_64 musl tar.gz）",
    "开发",
    "jj-vcs/jj",
    installer_markers_match_all=True,
    installer_markers=["jj-v", "x86_64-unknown-linux-musl.tar.gz"],
    href_exclude_substrings=["aarch64", "docs", "windows", "darwin", "apple"],
    installer_extensions=[".tar.gz"],
)

# --- UniGetUI 补 macOS / Linux（Windows 已有，脚本内另改路径）---
_entry(
    "darwin",
    "16-系统.json",
    "unigetui",
    "UniGetUI（包管理 GUI；macOS Apple Silicon dmg；原 WingetUI，现 Devolutions/UniGetUI）",
    "系统",
    "Devolutions/UniGetUI",
    installer_markers_match_all=True,
    installer_markers=["UniGetUI.macos-arm64", ".dmg"],
    href_exclude_substrings=["x64", ".tar.gz", ".zip", "checksum"],
    installer_extensions=[".dmg"],
)
_entry(
    "linux",
    "16-系统.json",
    "unigetui",
    "UniGetUI（包管理 GUI；Linux x64 deb；原 WingetUI，现 Devolutions/UniGetUI）",
    "系统",
    "Devolutions/UniGetUI",
    installer_markers_match_all=True,
    installer_markers=["UniGetUI.linux-x64", ".deb"],
    href_exclude_substrings=["arm64", ".rpm", ".tar.gz", ".zip", "checksum"],
    installer_extensions=[".deb"],
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
            # UniGetUI darwin/linux：允许同 id 跨平台；Windows 已有时 skip windows
            if aid in seen_ids or aid in file_ids:
                skipped += 1
                continue
            if rp in seen_repos and aid != "unigetui":
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


def _patch_repo_paths(dry: bool) -> int:
    """修正已迁移仓库路径。"""
    patches = [
        ("windows", "16-系统.json", "unigetui", "Devolutions/UniGetUI"),
        ("windows", "30-代理与隧道.json", "hiddify_next", "hiddify/hiddify-app"),
        ("darwin", "30-代理与隧道.json", "hiddify_next", "hiddify/hiddify-app"),
        ("linux", "30-代理与隧道.json", "hiddify_next", "hiddify/hiddify-app"),
    ]
    n = 0
    for plat, shard, aid, new_repo in patches:
        path = os.path.join(APPS, plat, shard)
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        changed = False
        for item in data:
            if not isinstance(item, dict) or item.get("id") != aid:
                continue
            old = item.get("repo_path") or ""
            if old.lower() == new_repo.lower():
                continue
            item["repo_path"] = new_repo
            item["releases_url"] = f"https://bgithub.xyz/{new_repo}/releases"
            if aid == "unigetui":
                item["简介"] = "UniGetUI（Winget / Scoop 等的图形化软件包管理前端；原 WingetUI，现 Devolutions/UniGetUI）"
            if aid == "hiddify_next":
                # 保持 id，仓库已迁到 hiddify-app
                intro = item.get("简介") or ""
                if "hiddify-app" not in intro.lower():
                    item["简介"] = intro.replace("Hiddify Next", "Hiddify（原 Hiddify Next / hiddify-app）")
            changed = True
            n += 1
            print(f"patch {plat}/{shard} {aid}: {old} -> {new_repo}")
        if changed and not dry:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
    return n


def main():
    dry = "--dry-run" in sys.argv
    a1, s1 = _merge_desktop(dry)
    p1 = _patch_repo_paths(dry)
    print(f"{'dry-run' if dry else 'done'}: desktop +{a1} skip {s1}; patches {p1}")


if __name__ == "__main__":
    main()
