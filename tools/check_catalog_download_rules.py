#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""扫描清单：GitHub Release 有资产但规则匹配不到（heu_kms 类问题）。"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import requests  # noqa: E402

from auto_update import (  # noqa: E402
    asset_targets_app,
    uses_docker_desktop,
    uses_github_pages_manifest,
    uses_go_dev_json,
)

SKIP_RESOLVE = frozenset(
    {
        "github_pages_manifest",
        "go_dev_json",
        "docker_desktop",
    }
)


def iter_apps(apps_dir: Path):
    for plat_dir in sorted(apps_dir.iterdir()):
        if not plat_dir.is_dir():
            continue
        platform = plat_dir.name
        for shard in sorted(plat_dir.glob("*.json")):
            with shard.open(encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                continue
            for app in data:
                app = dict(app)
                app["_platform"] = platform
                app["_shard"] = shard.name
                yield app


def uses_special_resolve(app: dict) -> bool:
    rv = (app.get("resolve_via") or "").strip().lower()
    return rv in SKIP_RESOLVE or uses_github_pages_manifest(app) or uses_go_dev_json(
        app
    ) or uses_docker_desktop(app)


def is_risky_static(app: dict) -> bool:
    if not (app.get("repo_path") or "").strip():
        return False
    if uses_special_resolve(app):
        return False
    if app.get("installer_markers"):
        return False
    if app.get("download_url_templates"):
        return False
    return True


def fetch_release(repo: str, cache: dict, verify: bool = False) -> dict | None:
    if repo in cache:
        return cache[repo]
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        r = requests.get(
            url,
            headers={
                "User-Agent": "gh-release-fetch-catalog-audit",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=25,
            verify=verify,
        )
        if r.status_code == 404:
            cache[repo] = None
            return None
        r.raise_for_status()
        data = r.json()
        cache[repo] = data
        return data
    except requests.RequestException as e:
        cache[repo] = {"_error": str(e)}
        return cache[repo]


def audit_apps(apps_list: list[dict], verify: bool = False) -> list[dict]:
    cache: dict = {}
    issues: list[dict] = []
    risky = [a for a in apps_list if is_risky_static(a)]

    for i, app in enumerate(risky):
        repo = app["repo_path"].strip()
        rel = fetch_release(repo, cache, verify=verify)
        if rel is None:
            issues.append(
                {
                    "kind": "no_release",
                    "id": app["id"],
                    "platform": app["_platform"],
                    "shard": app["_shard"],
                    "repo": repo,
                }
            )
            continue
        if rel.get("_error"):
            issues.append(
                {
                    "kind": "api_error",
                    "id": app["id"],
                    "platform": app["_platform"],
                    "shard": app["_shard"],
                    "repo": repo,
                    "error": rel["_error"],
                }
            )
            time.sleep(0.3)
            continue

        assets = rel.get("assets") or []
        tag = rel.get("tag_name") or rel.get("name") or "?"
        matched = [
            a.get("name")
            for a in assets
            if asset_targets_app(a.get("name") or "", a.get("browser_download_url") or "", app)
        ]
        if assets and not matched:
            issues.append(
                {
                    "kind": "asset_mismatch",
                    "id": app["id"],
                    "platform": app["_platform"],
                    "shard": app["_shard"],
                    "repo": repo,
                    "tag": tag,
                    "hint": app.get("url_hint") or app["id"],
                    "exts": app.get("installer_extensions") or [],
                    "assets": [a.get("name") for a in assets[:8]],
                    "asset_count": len(assets),
                }
            )
        elif not assets:
            issues.append(
                {
                    "kind": "no_assets",
                    "id": app["id"],
                    "platform": app["_platform"],
                    "shard": app["_shard"],
                    "repo": repo,
                    "tag": tag,
                }
            )
        time.sleep(0.15)

    return issues


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="检查清单下载规则是否与 GitHub Release 资产匹配")
    ap.add_argument(
        "--apps-dir",
        default="apps",
        help="apps 或 apps-mobile（默认 apps）",
    )
    ap.add_argument("--platform", default="", help="仅检查某平台，如 windows")
    ap.add_argument("--kind", default="", help="仅输出某类： asset_mismatch | no_assets | no_release")
    args = ap.parse_args()

    apps_dir = ROOT / args.apps_dir
    apps = list(iter_apps(apps_dir))
    if args.platform:
        apps = [a for a in apps if a["_platform"] == args.platform.strip().lower()]

    risky_static = [a for a in apps if is_risky_static(a)]
    print(f"扫描 {apps_dir.name}/ 共 {len(apps)} 条；无 installer_markers 且非特殊解析：{len(risky_static)} 条")
    print("正在请求 GitHub API（按 repo 去重缓存）…\n")

    issues = audit_apps(apps)
    if args.kind:
        issues = [x for x in issues if x["kind"] == args.kind]

    by_kind: dict[str, list] = {}
    for it in issues:
        by_kind.setdefault(it["kind"], []).append(it)

    labels = {
        "asset_mismatch": "有 Release 资产但规则匹配不到（heu_kms 类）",
        "no_assets": "最新 Release 无 assets（仅源码/tag）",
        "no_release": "无 latest release",
        "api_error": "API 请求失败",
    }
    for kind, rows in sorted(by_kind.items()):
        print(f"## {labels.get(kind, kind)} ({len(rows)})")
        for r in rows:
            if kind == "asset_mismatch":
                exts = ",".join(r["exts"]) or "(默认)"
                assets = ", ".join(r["assets"][:4])
                if r["asset_count"] > 4:
                    assets += f" …共{r['asset_count']}个"
                print(
                    f"  [{r['platform']}] {r['id']:28} {r['repo']}"
                    f"\n      tag={r['tag']} hint={r['hint']} exts={exts}"
                    f"\n      assets: {assets}"
                )
            elif kind == "no_assets":
                print(f"  [{r['platform']}] {r['id']:28} {r['repo']} tag={r['tag']}")
            else:
                extra = f" — {r.get('error', '')}" if r.get("error") else ""
                print(f"  [{r['platform']}] {r['id']:28} {r['repo']}{extra}")
        print()

    print(f"合计问题 {len(issues)} 条（不含已修复、未跑到的条目）")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
