# -*- coding: utf-8 -*-
"""判断应用是否可由本工具链下载，以及应打开的 fallback 页面。"""
from __future__ import annotations

import webbrowser


def _brief_suggests_no_binary(brief: str) -> bool:
    markers = (
        "勿启用",
        "仅作定位",
        "不适合本项目",
        "通过 pip",
        "通过 PyPI",
        "npm 安装",
        "App Store",
        "Microsoft Store",
        "无 GitHub Release 二进制",
        "无固定 GitHub Release",
        "需 clone",
        "官网获取",
    )
    return any(m in brief for m in markers)


def is_app_downloadable(app: dict) -> bool:
    """是否应尝试走 auto_update 下载（而非仅打开页面）。"""
    if app.get("open_page_only") is True:
        return False
    if (app.get("manifest_item_id") or "").strip():
        return True
    if app.get("installer_markers") or app.get("download_names") or app.get("download_url_templates"):
        return True
    if (app.get("resolve_via") or "").strip():
        return True
    brief = (app.get("简介") or "").strip()
    if _brief_suggests_no_binary(brief):
        return False
    if app.get("prefer_api_assets") and (app.get("repo_path") or "").strip():
        return True
    return False


def resolve_open_page_url(app: dict) -> str:
    """打开页面时优先用 open_page_url，否则 GitHub Releases / releases_url。"""
    explicit = (app.get("open_page_url") or "").strip()
    if explicit:
        return explicit
    releases = (app.get("releases_url") or "").strip()
    if releases:
        return releases.replace("bgithub.xyz", "github.com")
    repo = (app.get("repo_path") or "").strip().strip("/")
    if repo:
        return f"https://github.com/{repo}/releases"
    return ""


def open_page(url: str) -> bool:
    url = (url or "").strip()
    if not url:
        return False
    try:
        webbrowser.open(url)
        return True
    except OSError:
        return False


def action_label_for_app(app: dict) -> str:
    return "可下载" if is_app_downloadable(app) else "仅页面"
