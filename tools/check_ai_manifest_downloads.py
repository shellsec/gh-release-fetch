#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查 manifest 中 AI/编辑器 条目的下载 URL 是否可访问。"""
import json
import ssl
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads(
    (ROOT / "VibeCodingToolsDown/dist/vibecoding/manifest.json").read_text(encoding="utf-8")
)
AI_IDS = {
    "cursor", "trae", "trae_cn", "trae_solo", "qoder", "qoderwork", "zcode",
    "codebuddy", "codebuddy_cn", "workbuddy", "antigravity", "kiro",
    "windsurf", "lmstudio",
}
ctx = ssl.create_default_context()
UA = {"User-Agent": "gh-release-fetch-audit"}


def check(url: str) -> tuple[int | None, str]:
    if not url:
        return None, "null"
    req = urllib.request.Request(url, method="HEAD", headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
            return r.status, "ok"
    except urllib.error.HTTPError as e:
        # some CDNs reject HEAD
        if e.code in (403, 405):
            req2 = urllib.request.Request(url, headers={**UA, "Range": "bytes=0-0"})
            try:
                with urllib.request.urlopen(req2, timeout=25, context=ctx) as r:
                    return r.status, "range-ok"
            except Exception as e2:
                return e.code, str(e2)[:80]
        return e.code, str(e)[:80]
    except Exception as e:
        return None, str(e)[:80]


print(f"manifest generated_at: {manifest.get('generated_at')}\n")
for item in manifest["items"]:
    iid = item["id"]
    if iid not in AI_IDS:
        continue
    ver = item.get("version")
    print(f"## {iid}  v{ver}")
    notes = (item.get("notes") or "")[:100]
    if notes:
        print(f"   notes: {notes}...")
    dl = item.get("downloads") or {}
    for plat in ("windows", "darwin", "linux"):
        blk = dl.get(plat)
        if not blk or not blk.get("url"):
            print(f"   [{plat}] — 无下载链")
            continue
        url = blk["url"]
        code, msg = check(url)
        flag = "OK" if code in (200, 206) or msg in ("ok", "range-ok") else "FAIL"
        print(f"   [{plat}] {flag} HTTP {code}  {blk.get('filename')}")
        if flag == "FAIL":
            print(f"          {msg}")
    print()
