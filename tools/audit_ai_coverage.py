#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""仅审计 apps/*/01-AI.json 与 26-编辑器.json 中 AI IDE 条目。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.check_catalog_download_rules import audit_apps, is_risky_static, iter_apps, uses_special_resolve

AI_SHARDS = {"01-AI.json", "26-编辑器.json"}
AI_EDITOR_IDS = {
    "cursor", "trae", "trae_cn", "trae_solo", "qoder", "qoderwork", "zcode",
    "codebuddy", "codebuddy_cn", "workbuddy", "antigravity", "windsurf", "void_editor",
    "zed", "pearai",
}


def is_ai_entry(app: dict) -> bool:
    shard = app.get("_shard", "")
    if shard not in AI_SHARDS:
        return False
    if shard == "26-编辑器.json":
        return app.get("id") in AI_EDITOR_IDS or app.get("manifest_item_id")
    return True


apps_dir = ROOT / "apps"
apps = [a for a in iter_apps(apps_dir) if is_ai_entry(a)]

risky = [a for a in apps if is_risky_static(a)]
manifest = [a for a in apps if uses_special_resolve(a) and (a.get("manifest_item_id") or "manifest" in (a.get("resolve_via") or ""))]

print(f"AI 相关条目: {len(apps)}（manifest/special: {len(manifest)}，无 markers 风险: {len(risky)}）\n")

# platform parity for 01-AI ids
by_id: dict[str, set[str]] = {}
for a in apps:
    if a["_shard"] != "01-AI.json":
        continue
    by_id.setdefault(a["id"], set()).add(a["_platform"])

all_plats = {"windows", "darwin", "linux"}
print("=== 01-AI 三平台不齐 ===")
for iid, plats in sorted(by_id.items()):
    missing = all_plats - plats
    if missing:
        print(f"  {iid}: 缺 {','.join(sorted(missing))}")

print("\n=== 无 markers / 特殊解析 风险项 ===")
for a in sorted(risky, key=lambda x: (x["_platform"], x["id"])):
    print(f"  [{a['_platform']}] {a['id']:28} {a.get('repo_path','')}")

print("\n=== GitHub API 审计（01-AI + AI 编辑器）===")
issues = audit_apps(apps)
by_kind: dict[str, list] = {}
for it in issues:
    by_kind.setdefault(it["kind"], []).append(it)

for kind in ("asset_mismatch", "no_assets", "no_release", "api_error"):
    rows = by_kind.get(kind, [])
    if not rows:
        continue
    print(f"\n## {kind} ({len(rows)})")
    for r in rows[:40]:
        if kind == "asset_mismatch":
            print(f"  [{r['platform']}] {r['id']:28} tag={r['tag']}")
            print(f"      assets: {', '.join(r['assets'][:5])}")
        elif kind == "no_assets":
            print(f"  [{r['platform']}] {r['id']:28} tag={r['tag']}")
        else:
            print(f"  [{r['platform']}] {r['id']:28} {r.get('error','')}")
    if len(rows) > 40:
        print(f"  ... +{len(rows)-40} more")

print(f"\n合计问题 {len(issues)}")
