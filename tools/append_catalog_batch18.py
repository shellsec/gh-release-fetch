#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Batch18：AI 分片补缺（有 GitHub Release 二进制、尚未入库）。"""
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


SH = "01-AI.json"

# --- Qwen Code CLI ---
_e("windows", SH, "qwen_code",
   "Qwen Code（通义 Qwen 官方 coding agent CLI；Windows x64 zip）", "AI",
   "QwenLM/qwen-code",
   installer_markers_match_all=True,
   installer_markers=["qwen-code-win-x64", ".zip"],
   href_exclude_substrings=["darwin", "linux", "arm64", ".sig"],
   installer_extensions=[".zip"])
_e("darwin", SH, "qwen_code",
   "Qwen Code（macOS Apple Silicon tar.gz）", "AI",
   "QwenLM/qwen-code",
   installer_markers_match_all=True,
   installer_markers=["qwen-code-darwin-arm64", ".tar.gz"],
   href_exclude_substrings=["x64", "linux", "win-x64", ".sig"],
   installer_extensions=[".tar.gz"])
_e("linux", SH, "qwen_code",
   "Qwen Code（Linux x64 tar.gz）", "AI",
   "QwenLM/qwen-code",
   installer_markers_match_all=True,
   installer_markers=["qwen-code-linux-x64", ".tar.gz"],
   href_exclude_substrings=["arm64", "darwin", "win", ".sig"],
   installer_extensions=[".tar.gz"])

# --- Kimi CLI ---
_e("windows", SH, "kimi_cli",
   "Kimi CLI（Moonshot 官方命令行；Windows x64 zip）", "AI",
   "moonshotai/kimi-cli",
   installer_markers_match_all=True,
   installer_markers=["x86_64-pc-windows-msvc.zip"],
   href_exclude_substrings=["onedir", "aarch64", "linux", "darwin", "apple"],
   installer_extensions=[".zip"])
_e("darwin", SH, "kimi_cli",
   "Kimi CLI（macOS Apple Silicon tar.gz）", "AI",
   "moonshotai/kimi-cli",
   installer_markers_match_all=True,
   installer_markers=["aarch64-apple-darwin.tar.gz"],
   href_exclude_substrings=["onedir", "x86_64", "windows", "linux"],
   installer_extensions=[".tar.gz"])
_e("linux", SH, "kimi_cli",
   "Kimi CLI（Linux x86_64 tar.gz）", "AI",
   "moonshotai/kimi-cli",
   installer_markers_match_all=True,
   installer_markers=["x86_64-unknown-linux-gnu.tar.gz"],
   href_exclude_substrings=["onedir", "aarch64", "windows", "darwin", "apple"],
   installer_extensions=[".tar.gz"])

# --- Claude Code Router 桌面 ---
_e("windows", SH, "claude_code_router",
   "Claude Code Router（多模型路由桌面端；Windows exe）", "AI",
   "musistudio/claude-code-router",
   installer_markers_match_all=True,
   installer_markers=["Claude-Code-Router_", ".exe"],
   href_exclude_substrings=["AppImage", ".dmg", ".zip", "arm64", "mac", "linux"],
   installer_extensions=[".exe"], windows_installer=True, run_installer=True)
_e("darwin", SH, "claude_code_router",
   "Claude Code Router（macOS Apple Silicon dmg）", "AI",
   "musistudio/claude-code-router",
   installer_markers_match_all=True,
   installer_markers=["Claude-Code-Router_", "Apple-Silicon-arm64.dmg"],
   href_exclude_substrings=["Intel", ".zip", ".exe", "AppImage"],
   installer_extensions=[".dmg"])
_e("linux", SH, "claude_code_router",
   "Claude Code Router（Linux AppImage）", "AI",
   "musistudio/claude-code-router",
   installer_markers_match_all=True,
   installer_markers=["Claude-Code-Router_", ".AppImage"],
   href_exclude_substrings=[".exe", ".dmg", ".zip", "mac"],
   installer_extensions=[".AppImage"])

# --- KoboldCpp ---
_e("windows", SH, "koboldcpp",
   "KoboldCpp（本地 LLM 推理前端；Windows CUDA 版 exe）", "AI",
   "LostRuins/koboldcpp",
   installer_markers_match_all=True,
   installer_markers=["koboldcpp.exe"],
   href_exclude_substrings=["nocuda", "oldpc", "rocm", ".zip"],
   installer_extensions=[".exe"])

# --- llamafile ---
_e("windows", SH, "llamafile",
   "llamafile（Mozilla 单文件本地 LLM 运行器；跨平台 zip）", "AI",
   "Mozilla-Ocho/llamafile",
   installer_markers_match_all=True,
   installer_markers=["llamafile-", ".zip"],
   href_exclude_substrings=[".sig", "sha256"],
   installer_extensions=[".zip"])
_e("darwin", SH, "llamafile",
   "llamafile（Mozilla 单文件本地 LLM 运行器；跨平台 zip）", "AI",
   "Mozilla-Ocho/llamafile",
   installer_markers_match_all=True,
   installer_markers=["llamafile-", ".zip"],
   href_exclude_substrings=[".sig", "sha256"],
   installer_extensions=[".zip"])
_e("linux", SH, "llamafile",
   "llamafile（Mozilla 单文件本地 LLM 运行器；跨平台 zip）", "AI",
   "Mozilla-Ocho/llamafile",
   installer_markers_match_all=True,
   installer_markers=["llamafile-", ".zip"],
   href_exclude_substrings=[".sig", "sha256"],
   installer_extensions=[".zip"])

# --- llama.cpp CPU 包 ---
_e("windows", SH, "llama_cpp",
   "llama.cpp（GGML 本地推理；Windows CPU x64 zip，CUDA 包另选）", "AI",
   "ggml-org/llama.cpp",
   installer_markers_match_all=True,
   installer_markers=["bin-win-cpu-x64", ".zip"],
   href_exclude_substrings=["cuda", "vulkan", "sycl", "rocm", "openvino", "arm64", "cudart"],
   installer_extensions=[".zip"])
_e("darwin", SH, "llama_cpp",
   "llama.cpp（macOS Apple Silicon tar.gz）", "AI",
   "ggml-org/llama.cpp",
   installer_markers_match_all=True,
   installer_markers=["bin-macos-arm64", ".tar.gz"],
   href_exclude_substrings=["x64", "android", "ubuntu", "win-", "ui.tar"],
   installer_extensions=[".tar.gz"])
_e("linux", SH, "llama_cpp",
   "llama.cpp（Linux x64 tar.gz）", "AI",
   "ggml-org/llama.cpp",
   installer_markers_match_all=True,
   installer_markers=["bin-ubuntu-x64", ".tar.gz"],
   href_exclude_substrings=["vulkan", "sycl", "openvino", "arm64", "s390x", "win", "macos"],
   installer_extensions=[".tar.gz"])

# --- LocalAI ---
_e("darwin", SH, "local_ai",
   "LocalAI（本地 OpenAI 兼容 API；macOS dmg）", "AI",
   "mudler/LocalAI",
   installer_markers_match_all=True,
   installer_markers=["LocalAI", ".dmg"],
   href_exclude_substrings=["linux", ".tar", ".exe"],
   installer_extensions=[".dmg"])
_e("linux", SH, "local_ai",
   "LocalAI（本地 OpenAI 兼容 API；Linux launcher tar.xz）", "AI",
   "mudler/LocalAI",
   installer_markers_match_all=True,
   installer_markers=["local-ai-launcher-linux", ".tar.xz"],
   href_exclude_substrings=[".dmg", ".exe"],
   installer_extensions=[".tar.xz"])

# --- Pinokio ---
_e("windows", SH, "pinokio",
   "Pinokio（一键跑本地 AI 应用的浏览器式桌面；Windows exe）", "AI",
   "pinokiocomputer/pinokio",
   installer_markers_match_all=True,
   installer_markers=["Pinokio.exe"],
   href_exclude_substrings=["AppImage", ".dmg", ".deb", ".rpm", ".zip", "arm64"],
   installer_extensions=[".exe"], windows_installer=True, run_installer=True)
_e("darwin", SH, "pinokio",
   "Pinokio（macOS Apple Silicon dmg）", "AI",
   "pinokiocomputer/pinokio",
   installer_markers_match_all=True,
   installer_markers=["Pinokio-", "arm64.dmg"],
   href_exclude_substrings=[".zip", ".exe", "AppImage", ".deb"],
   installer_extensions=[".dmg"])
_e("linux", SH, "pinokio",
   "Pinokio（Linux x64 AppImage）", "AI",
   "pinokiocomputer/pinokio",
   installer_markers_match_all=True,
   installer_markers=["Pinokio-", ".AppImage"],
   href_exclude_substrings=["arm64", ".deb", ".rpm", ".dmg", ".exe", ".zip"],
   installer_extensions=[".AppImage"])

# --- Open Interpreter ---
_e("windows", SH, "open_interpreter",
   "Open Interpreter（自然语言操控本机；Windows x64 tar.gz）", "AI",
   "OpenInterpreter/open-interpreter",
   installer_markers_match_all=True,
   installer_markers=["open-interpreter-package-x86_64-pc-windows-msvc", ".tar.gz"],
   href_exclude_substrings=["aarch64", "linux", "darwin", "apple"],
   installer_extensions=[".tar.gz"])
_e("darwin", SH, "open_interpreter",
   "Open Interpreter（macOS Apple Silicon tar.gz）", "AI",
   "OpenInterpreter/open-interpreter",
   installer_markers_match_all=True,
   installer_markers=["open-interpreter-package-aarch64-apple-darwin", ".tar.gz"],
   href_exclude_substrings=["x86_64", "windows", "linux"],
   installer_extensions=[".tar.gz"])
_e("linux", SH, "open_interpreter",
   "Open Interpreter（Linux x86_64 musl tar.gz）", "AI",
   "OpenInterpreter/open-interpreter",
   installer_markers_match_all=True,
   installer_markers=["open-interpreter-package-x86_64-unknown-linux-musl", ".tar.gz"],
   href_exclude_substrings=["aarch64", "windows", "darwin", "apple"],
   installer_extensions=[".tar.gz"])

# --- ChatALL ---
_e("windows", SH, "chatall",
   "ChatALL（同时问多家大模型的桌面客户端；Windows x64 安装包）", "AI",
   "sunner/ChatALL",
   installer_markers_match_all=True,
   installer_markers=["ChatALL-", "win-x64.exe"],
   href_exclude_substrings=["arm64", "win.exe", ".zip", "mac", "linux"],
   installer_extensions=[".exe"], windows_installer=True, run_installer=True)
_e("darwin", SH, "chatall",
   "ChatALL（macOS Apple Silicon dmg）", "AI",
   "sunner/ChatALL",
   installer_markers_match_all=True,
   installer_markers=["ChatALL-", "mac-arm64.dmg"],
   href_exclude_substrings=["x64", ".zip", "win", "linux"],
   installer_extensions=[".dmg"])
_e("linux", SH, "chatall",
   "ChatALL（Linux x86_64 AppImage）", "AI",
   "sunner/ChatALL",
   installer_markers_match_all=True,
   installer_markers=["ChatALL-", "linux-x86_64.AppImage"],
   href_exclude_substrings=["arm64", ".deb", "win", "mac"],
   installer_extensions=[".AppImage"])

# --- mods / fabric ---
_e("windows", SH, "mods",
   "mods（Charm 终端 AI；Windows x64 zip）", "AI",
   "charmbracelet/mods",
   installer_markers_match_all=True,
   installer_markers=["mods_", "Windows_x86_64.zip"],
   href_exclude_substrings=["arm64", "Linux", "Darwin", ".deb", ".rpm", ".tar.gz"],
   installer_extensions=[".zip"])
_e("darwin", SH, "mods",
   "mods（Charm 终端 AI；macOS Apple Silicon tar.gz）", "AI",
   "charmbracelet/mods",
   installer_markers_match_all=True,
   installer_markers=["mods_", "Darwin_arm64.tar.gz"],
   href_exclude_substrings=["x86_64", "Windows", "Linux", ".deb", ".rpm"],
   installer_extensions=[".tar.gz"])
_e("linux", SH, "mods",
   "mods（Charm 终端 AI；Linux x86_64 tar.gz）", "AI",
   "charmbracelet/mods",
   installer_markers_match_all=True,
   installer_markers=["mods_", "Linux_x86_64.tar.gz"],
   href_exclude_substrings=["arm64", "Windows", "Darwin", ".deb", ".rpm", "i386"],
   installer_extensions=[".tar.gz"])

_e("windows", SH, "fabric",
   "fabric（AI 提示词工作流 CLI；Windows x64 zip）", "AI",
   "danielmiessler/fabric",
   installer_markers_match_all=True,
   installer_markers=["fabric_Windows_x86_64", ".zip"],
   href_exclude_substrings=["arm64", "i386", "Linux", "Darwin"],
   installer_extensions=[".zip"])
_e("darwin", SH, "fabric",
   "fabric（macOS Apple Silicon tar.gz）", "AI",
   "danielmiessler/fabric",
   installer_markers_match_all=True,
   installer_markers=["fabric_Darwin_arm64", ".tar.gz"],
   href_exclude_substrings=["x86_64", "Windows", "Linux"],
   installer_extensions=[".tar.gz"])
_e("linux", SH, "fabric",
   "fabric（Linux x86_64 tar.gz）", "AI",
   "danielmiessler/fabric",
   installer_markers_match_all=True,
   installer_markers=["fabric_Linux_x86_64", ".tar.gz"],
   href_exclude_substrings=["arm64", "i386", "Windows", "Darwin"],
   installer_extensions=[".tar.gz"])

# --- Magika / Piper ---
_e("windows", SH, "magika",
   "Magika（Google 开源文件类型识别 CLI；Windows x64 zip）", "AI",
   "google/magika",
   installer_markers_match_all=True,
   installer_markers=["magika-cli-x86_64-pc-windows-msvc", ".zip"],
   href_exclude_substrings=["linux", "darwin", "apple", "aarch64"],
   installer_extensions=[".zip"])
_e("darwin", SH, "magika",
   "Magika（macOS Apple Silicon tar.xz）", "AI",
   "google/magika",
   installer_markers_match_all=True,
   installer_markers=["magika-cli-aarch64-apple-darwin", ".tar.xz"],
   href_exclude_substrings=["linux", "windows", "x86_64"],
   installer_extensions=[".tar.xz"])
_e("linux", SH, "magika",
   "Magika（Linux x86_64 tar.xz）", "AI",
   "google/magika",
   installer_markers_match_all=True,
   installer_markers=["magika-cli-x86_64-unknown-linux-gnu", ".tar.xz"],
   href_exclude_substrings=["windows", "darwin", "apple", "aarch64"],
   installer_extensions=[".tar.xz"])

_e("windows", SH, "piper",
   "Piper（本地神经网络 TTS；Windows amd64 zip）", "AI",
   "rhasspy/piper",
   installer_markers_match_all=True,
   installer_markers=["piper_windows_amd64", ".zip"],
   href_exclude_substrings=["linux", "macos"],
   installer_extensions=[".zip"])
_e("darwin", SH, "piper",
   "Piper（macOS Apple Silicon tar.gz）", "AI",
   "rhasspy/piper",
   installer_markers_match_all=True,
   installer_markers=["piper_macos_aarch64", ".tar.gz"],
   href_exclude_substrings=["x64", "linux", "windows"],
   installer_extensions=[".tar.gz"])
_e("linux", SH, "piper",
   "Piper（Linux x86_64 tar.gz）", "AI",
   "rhasspy/piper",
   installer_markers_match_all=True,
   installer_markers=["piper_linux_x86_64", ".tar.gz"],
   href_exclude_substrings=["aarch64", "armv7", "macos", "windows"],
   installer_extensions=[".tar.gz"])


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
