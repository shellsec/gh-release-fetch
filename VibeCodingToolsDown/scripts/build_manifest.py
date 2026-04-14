#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
聚合各官网 / 官方 API 的下载直链，生成 VibeCodingToolsDown/dist/vibecoding/manifest.json。
供 GitHub Pages 发布；auto_update.py 通过 resolve_via=github_pages_manifest 读取。

仅依赖 requests、beautifulsoup4（与仓库 requirements.txt 一致）。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import copy
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/html;q=0.9,*/*;q=0.8",
}
GH_ACCEPT = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}


def _session():
    s = requests.Session()
    s.headers.update(UA)
    return s


def _item(
    item_id: str,
    version: str,
    downloads: dict[str, dict[str, str] | None],
    notes: str | None = None,
) -> dict[str, Any]:
    return {
        "id": item_id,
        "version": version.lstrip("v"),
        "version_tag": version if version.startswith("v") else f"v{version}",
        "downloads": downloads,
        "notes": notes,
    }


def fetch_cursor(s: requests.Session) -> dict[str, Any]:
    r = s.get(
        "https://api.github.com/repos/accesstechnology-mike/cursor-downloads/releases/latest",
        headers=GH_ACCEPT,
        timeout=40,
    )
    r.raise_for_status()
    j = r.json()
    tag = (j.get("tag_name") or "").strip() or "unknown"
    ver = tag.lstrip("v")
    body = j.get("body") or ""
    urls = re.findall(r"\((https://downloads\.cursor\.com[^)]+)\)", body)
    win = next((u for u in urls if "UserSetup-x64" in u and u.lower().endswith(".exe")), None)
    mac_u = next((u for u in urls if "darwin-universal" in u and u.lower().endswith(".zip")), None)
    mac_a = next((u for u in urls if "darwin-arm64" in u and u.lower().endswith(".zip")), None)
    mac_i = next((u for u in urls if "darwin-x64" in u and u.lower().endswith(".zip")), None)
    lin = next(
        (
            u
            for u in urls
            if "linux" in u and "x86_64" in u and u.lower().endswith(".appimage") and ".zsync" not in u.lower()
        ),
        None,
    )
    return _item(
        "cursor",
        ver,
        {
            "windows": {"url": win, "filename": os.path.basename(win) if win else ""} if win else None,
            "darwin": {"url": mac_u or mac_a, "filename": os.path.basename(mac_u or mac_a or "")}
            if (mac_u or mac_a)
            else None,
            "linux": {"url": lin, "filename": os.path.basename(lin) if lin else ""} if lin else None,
        },
        notes="索引自 accesstechnology-mike/cursor-downloads Release 正文中的官方 CDN 链。",
    )


def _vscode_redirect(s: requests.Session, path_suffix: str) -> str:
    """使用微软官方 update 通道解析最终下载 URL（HEAD 跟随重定向）。"""
    u = "https://update.code.visualstudio.com/" + path_suffix.lstrip("/")
    r = s.head(u, allow_redirects=True, timeout=40)
    r.raise_for_status()
    return r.url


def fetch_vscode(s: requests.Session) -> dict[str, Any]:
    r = s.get(
        "https://api.github.com/repos/microsoft/vscode/releases/latest",
        headers=GH_ACCEPT,
        timeout=40,
    )
    r.raise_for_status()
    j = r.json()
    tag = (j.get("tag_name") or "").strip()
    ver = tag.lstrip("v")
    win_u = _vscode_redirect(s, "latest/win32-x64/stable")
    mac_u = _vscode_redirect(s, "latest/darwin-arm64/stable")
    lin_u = _vscode_redirect(s, "latest/linux-x64/stable")
    downloads = {
        "windows": {"url": win_u, "filename": os.path.basename(win_u.split("?", 1)[0])},
        "darwin": {"url": mac_u, "filename": os.path.basename(mac_u.split("?", 1)[0])},
        "linux": {"url": lin_u, "filename": os.path.basename(lin_u.split("?", 1)[0])},
    }
    return _item(
        "vscode",
        ver,
        downloads,
        notes="版本 tag 来自 GitHub API；安装包 URL 来自 update.code.visualstudio.com 重定向（微软官方）。",
    )


def fetch_vscodium(s: requests.Session) -> dict[str, Any]:
    r = s.get(
        "https://api.github.com/repos/VSCodium/vscodium/releases/latest",
        headers=GH_ACCEPT,
        timeout=40,
    )
    r.raise_for_status()
    j = r.json()
    tag = (j.get("tag_name") or "").strip()
    ver = tag.lstrip("v")
    assets = {a.get("name", ""): a.get("browser_download_url", "") for a in (j.get("assets") or [])}

    def pick(pred):
        for name, u in assets.items():
            if pred(name):
                return {"url": u, "filename": name}
        return None

    win = pick(lambda n: n.startswith("VSCodiumUserSetup-x64-") and n.endswith(".exe"))
    mac = pick(lambda n: n.startswith("VSCodium-darwin-arm64-") and n.endswith(".zip"))
    lin = pick(lambda n: n.startswith("VSCodium-linux-x64-") and n.endswith(".tar.gz"))
    return _item("vscodium", ver, {"windows": win, "darwin": mac, "linux": lin}, notes="GitHub API latest assets。")


def fetch_trae(s: requests.Session) -> dict[str, Any]:
    r = s.get("https://traeide.com/download", timeout=40)
    r.raise_for_status()
    urls = sorted(set(re.findall(r"https://lf-trae\.toscdn\.com[^\s\"'<>]+", r.text)))
    if not urls:
        raise RuntimeError("traeide.com/download 未找到 lf-trae 直链")
    ver = "unknown"
    m = re.search(r"/releases/stable/([^/]+)/", urls[0])
    if m:
        ver = m.group(1)

    def pick(sub):
        for u in urls:
            if sub in u:
                return {"url": u, "filename": os.path.basename(u.split("?", 1)[0])}
        return None

    win = pick("Trae-Setup-x64") or pick("win32")
    mac = pick("darwin-universal") or pick("darwin-arm64") or pick("darwin-x64")
    return _item(
        "trae",
        ver,
        {
            "windows": win,
            "darwin": mac,
            "linux": None,
        },
        notes="来自 traeide.com/download 静态页；国内 trae.cn 为 SPA，版本以字节 CDN 为准。",
    )


def fetch_trae_cn(s: requests.Session) -> dict[str, Any]:
    base = copy.deepcopy(fetch_trae(s))
    base["id"] = "trae_cn"
    base["notes"] = (
        "与 Trae 同源 CDN（traeide 文档页解析）。若需严格国内渠道请以 www.trae.cn 应用内/商店为准。"
    )
    return base


def fetch_antigravity(s: requests.Session) -> dict[str, Any]:
    """
    Antigravity 下载页为前端渲染，服务端抓取 HTML 通常不含直链。
    此处返回占位；可在后续接入官方 JSON 或 Playwright 再填充。
    """
    return _item(
        "antigravity",
        "0",
        {"windows": None, "darwin": None, "linux": None},
        notes="请从 https://antigravity.google/download 手动下载；自动化需可执行 JS 的环境。",
    )


def fetch_kiro(s: requests.Session) -> dict[str, Any]:
    r = s.get("https://prod.download.cli.kiro.dev/stable/latest/manifest.json", timeout=40)
    r.raise_for_status()
    j = r.json()
    ver = str(j.get("version") or "unknown")
    base_latest = "https://prod.download.cli.kiro.dev/stable/latest/"
    packages = j.get("packages") or []

    def pick_pkg(**kw):
        for p in packages:
            if not all(p.get(k) == v for k, v in kw.items()):
                continue
            rel = p.get("download") or ""
            fname = rel.split("/")[-1]
            if not fname:
                continue
            url = base_latest + quote(fname, safe="")
            return {"url": url, "filename": fname}
        return None

    return _item(
        "kiro",
        ver,
        {
            "windows": pick_pkg(
                os="windows", fileType="msi", variant="full", architecture="x86_64"
            ),
            "darwin": pick_pkg(
                os="macos", fileType="dmg", variant="full", architecture="universal"
            ),
            "linux": pick_pkg(
                os="linux", fileType="appImage", variant="full", architecture="x86_64"
            )
            or pick_pkg(os="linux", fileType="deb", variant="full", architecture="x86_64"),
        },
        notes="Kiro CLI 官方 manifest（含 Windows MSI / macOS dmg / Linux AppImage 等）。",
    )


def fetch_qoder(s: requests.Session) -> dict[str, Any]:
    """尽力从 Next 分片 JS 中提取直链；失败则返回占位版本。"""
    notes = []
    try:
        for page in ("https://qoder.com/zh/download", "https://qoder.com/en/download"):
            r = s.get(page, timeout=40)
            r.raise_for_status()
            html = r.text
            chunks = re.findall(
                r"https://g\.alicdn\.com/Qoder/qoder-web/[^\"']+/download/page-[a-z0-9]+\.js",
                html,
            )
            if not chunks:
                chunks = re.findall(
                    r"https://g\.alicdn\.com/Qoder/qoder-web/[^\"']+/%5Blang%5D/download/page-[a-z0-9]+\.js",
                    html,
                )
            if not chunks:
                continue
            ju = chunks[0].replace("\\u002F", "/")
            jr = s.get(ju, timeout=40)
            jr.raise_for_status()
            body = jr.text
            hits = sorted(
                set(
                    re.findall(
                        r"https://[a-zA-Z0-9./_?=&%-]{12,400}\.(?:exe|dmg|deb|rpm|AppImage)",
                        body,
                        flags=re.I,
                    )
                )
            )
            win = next((h for h in hits if h.lower().endswith(".exe")), None)
            mac = next((h for h in hits if h.lower().endswith(".dmg")), None)
            lin = next(
                (h for h in hits if h.lower().endswith((".deb", ".rpm", ".appimage"))),
                None,
            )
            if win or mac or lin:
                ver = "unknown"
                vm = re.search(r"Qoder[-_]?(\d+\.\d+\.\d+)", body, re.I)
                if vm:
                    ver = vm.group(1)
                return _item(
                    "qoder",
                    ver,
                    {
                        "windows": {"url": win, "filename": os.path.basename(win.split("?", 1)[0])}
                        if win
                        else None,
                        "darwin": {"url": mac, "filename": os.path.basename(mac.split("?", 1)[0])}
                        if mac
                        else None,
                        "linux": {"url": lin, "filename": os.path.basename(lin.split("?", 1)[0])}
                        if lin
                        else None,
                    },
                    notes=f"自 {page} 关联的 CDN JS 分片启发式解析。",
                )
    except Exception as e:
        notes.append(f"qoder 解析失败: {e}")
    return _item(
        "qoder",
        "0",
        {"windows": None, "darwin": None, "linux": None},
        notes="; ".join(notes) or "未能从官网静态资源解析 Qoder 安装包，请从 https://qoder.com/download 手动下载。",
    )


def fetch_codebuddy(s: requests.Session) -> dict[str, Any]:
    return _item(
        "codebuddy",
        "0",
        {"windows": None, "darwin": None, "linux": None},
        notes="国际版 CodeBuddy 下载多为动态加载，请从 https://www.codebuddy.ai/ 或文档安装页获取。",
    )


def fetch_codebuddy_cn(s: requests.Session) -> dict[str, Any]:
    return _item(
        "codebuddy_cn",
        "0",
        {"windows": None, "darwin": None, "linux": None},
        notes="国内版请从 https://copilot.tencent.com/ide/ 选择对应芯片安装包（页面为 SPA，未在此脚本硬编码直链）。",
    )


def main():
    ap = argparse.ArgumentParser(description="生成 VibeCodingToolsDown manifest.json")
    ap.add_argument(
        "--output-dir",
        default="",
        help="输出根目录（默认：本包根下 dist/）",
    )
    args = ap.parse_args()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 本脚本位于 …/scripts/，输出默认写入包根目录 dist/（与是否在主仓库内无关）
    vibe_root = os.path.normpath(os.path.join(script_dir, ".."))
    out_root = args.output_dir.strip() or os.path.join(vibe_root, "dist")
    out_dir = os.path.join(out_root, "vibecoding")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "manifest.json")

    s = _session()
    items: list[dict[str, Any]] = []
    builders = [
        fetch_cursor,
        fetch_vscode,
        fetch_vscodium,
        fetch_trae,
        fetch_trae_cn,
        fetch_qoder,
        fetch_codebuddy,
        fetch_codebuddy_cn,
        fetch_antigravity,
        fetch_kiro,
    ]
    errors: list[str] = []
    for fn in builders:
        try:
            items.append(fn(s))
        except Exception as e:
            errors.append(f"{fn.__name__}: {e}")

    doc = {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "items": items,
        "errors": errors,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    print("Wrote", out_path, "items", len(items), "errors", len(errors))
    if errors:
        for e in errors:
            print("WARN:", e, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
