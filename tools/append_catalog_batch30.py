#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Batch30：国内常用闭源头部（腾讯会议/TIM/腾讯文档 + Linux 企业微信）。仅 open_page_only。"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS = os.path.join(ROOT, "apps")
MOBILE = os.path.join(ROOT, "apps-mobile")
BATCH: dict[tuple[str, str], list] = {}
MOBILE_BATCH: dict[tuple[str, str], list] = {}


def _add(plat: str, shard: str, apps: list):
    BATCH.setdefault((plat, shard), []).extend(apps)


def _madd(plat: str, shard: str, apps: list):
    MOBILE_BATCH.setdefault((plat, shard), []).extend(apps)


def _page(aid, 简介, 分类, url, aliases, extra=None):
    d = {
        "id": aid,
        "简介": 简介,
        "分类": 分类,
        "aliases": list(aliases),
        "enabled": False,
        "open_page_only": True,
        "open_page_url": url,
        "url_hint": " ".join(aliases),
        "windows_installer": False,
        "process_name": "",
        "kill_before_install": False,
        "run_installer": False,
    }
    if extra:
        d.update(extra)
    return d


def _on(plats, shard, aid, 简介, 分类, url, aliases, urls=None):
    urls = urls or {}
    for plat in plats:
        _add(plat, shard, [_page(aid, 简介, 分类, urls.get(plat, url), aliases)])


WDL = ("windows", "darwin", "linux")
SH_OFF = "04-办公.json"
SH_IM = "20-网络与通讯.json"
SH_REMOTE = "21-远程与协作.json"

MEETING_URL = "https://meeting.tencent.com/download/"
DOCS_URL = "https://docs.qq.com/home/download"
TIM_URL = "https://tim.qq.com/download.html"
WECOM_URL = "https://work.weixin.qq.com/#indexDownload"
MEETING_IOS = "https://apps.apple.com/app/id1484048379"
TIM_IOS = "https://apps.apple.com/app/id1175213887"
DOCS_IOS = "https://apps.apple.com/app/id1370780836"

# --- 桌面：腾讯会议（Win/Mac/Linux 同一下载中心） ---
_on(
    WDL, SH_REMOTE, "tencent_meeting",
    "腾讯会议（官网分发，lookup 打开下载页）", "远程与协作",
    MEETING_URL,
    ["tencent_meeting", "腾讯会议", "wemeet", "WeMeet", "voov", "VooV"],
)

# --- 桌面：TIM（官网仅 Windows 客户端） ---
_on(
    ("windows",), SH_IM, "tim",
    "TIM（QQ 办公简洁版；官网分发，lookup 打开下载页）", "网络与通讯",
    TIM_URL,
    ["tim", "TIM", "QQ办公"],
)

# --- 桌面：腾讯文档 ---
_on(
    WDL, SH_OFF, "tencent_docs",
    "腾讯文档（在线协作 Office；官网分发，lookup 打开下载页）", "办公",
    DOCS_URL,
    ["tencent_docs", "腾讯文档", "docs.qq", "tdocs"],
)

# --- Linux 补企业微信（Win/Mac 已有） ---
_on(
    ("linux",), SH_IM, "wecom",
    "企业微信（官网分发，lookup 打开下载页）", "网络与通讯",
    WECOM_URL,
    ["wecom", "企业微信", "wework", "wxwork"],
)

# --- Android ---
_madd("android", SH_REMOTE, [_page(
    "tencent_meeting_android",
    "腾讯会议 Android（lookup 打开官网下载页）",
    "远程与协作", MEETING_URL,
    ["tencent_meeting", "腾讯会议", "wemeet", "WeMeet"],
)])
_madd("android", SH_IM, [_page(
    "tim_android",
    "TIM Android（lookup 打开官网下载页）",
    "网络与通讯", TIM_URL,
    ["tim", "TIM", "QQ办公"],
)])
_madd("android", SH_OFF, [_page(
    "tencent_docs_android",
    "腾讯文档 Android（lookup 打开官网下载页）",
    "办公", DOCS_URL,
    ["tencent_docs", "腾讯文档", "docs.qq"],
)])

# --- iOS（App Store） ---
def _ios(aid, name, 分类, url, aliases):
    return _page(
        aid,
        "%s（iOS · App Store；lookup 打开商店页，勿启用 auto_update）" % name,
        分类, url, aliases,
        extra={"releases_url": url},
    )


_madd("ios", SH_REMOTE, [_ios(
    "tencent_meeting_ios", "腾讯会议", "远程与协作",
    MEETING_IOS,
    ["tencent_meeting", "腾讯会议", "wemeet", "WeMeet"],
)])
_madd("ios", SH_IM, [_ios(
    "tim_ios", "TIM", "网络与通讯",
    TIM_IOS,
    ["tim", "TIM", "QQ办公"],
)])
_madd("ios", SH_OFF, [_ios(
    "tencent_docs_ios", "腾讯文档", "办公",
    DOCS_IOS,
    ["tencent_docs", "腾讯文档", "docs.qq"],
)])


def _load_ids(root: str, plat: str) -> set[str]:
    ids: set[str] = set()
    d = os.path.join(root, plat)
    if not os.path.isdir(d):
        return ids
    for fn in os.listdir(d):
        if not fn.endswith(".json"):
            continue
        with open(os.path.join(d, fn), encoding="utf-8") as f:
            for item in json.load(f):
                if isinstance(item, dict) and item.get("id"):
                    ids.add(item["id"].strip())
    return ids


def _merge(root: str, batch: dict, dry: bool) -> tuple[int, int]:
    added = skipped = 0
    plat_ids: dict[str, set[str]] = {}
    for (plat, shard), apps in sorted(batch.items()):
        path = os.path.join(root, plat, shard)
        data = json.load(open(path, encoding="utf-8")) if os.path.isfile(path) else []
        if plat not in plat_ids:
            plat_ids[plat] = _load_ids(root, plat)
        seen = plat_ids[plat]
        file_ids = {(a.get("id") or "").strip() for a in data if isinstance(a, dict)}
        for app in apps:
            aid = (app.get("id") or "").strip()
            if aid in seen or aid in file_ids:
                skipped += 1
                print(f"skip {plat}/{aid}")
                continue
            data.append(app)
            seen.add(aid)
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
    a1, s1 = _merge(APPS, BATCH, dry)
    a2, s2 = _merge(MOBILE, MOBILE_BATCH, dry)
    print(f"{'dry-run' if dry else 'done'}: desktop +{a1} skip {s1}; mobile +{a2} skip {s2}")


if __name__ == "__main__":
    main()
