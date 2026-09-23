#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Batch32：大厂头部 AI 门户补缺（open_page_only，官方域名，不硬编直链）。"""
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


def _ios(aid, name, 分类, url, aliases):
    return _page(
        aid,
        "%s（iOS · App Store；lookup 打开商店页，勿启用 auto_update）" % name,
        分类, url, aliases,
        extra={"releases_url": url},
    )


WDL = ("windows", "darwin", "linux")
WL = ("windows", "linux")
SH_AI = "01-AI.json"

# --- 微软 Copilot（darwin 已有 Mac App Store 条） ---
_on(
    WL, SH_AI, "copilot",
    "Microsoft Copilot（对话网页；lookup 打开官网。GitHub 编程助手见 github_copilot）",
    "AI",
    "https://copilot.microsoft.com/",
    ["copilot", "Copilot", "Microsoft Copilot", "微软Copilot"],
)

# --- 腾讯 ima（元宝/混元已在；元器平台不收） ---
_on(
    WDL, SH_AI, "ima",
    "ima（腾讯 AI 知识工作台网页；lookup 打开官网。C 端助手见 yuanbao）",
    "AI",
    "https://ima.qq.com/",
    ["ima", "腾讯ima", "ima.qq"],
)

# --- 字节 Cici（国内豆包已在；Trae 在 26-编辑器） ---
_on(
    WDL, SH_AI, "cici",
    "Cici / Dola（字节海外对话网页；lookup 打开官网。国内见 doubao）",
    "AI",
    "https://www.ciciai.com/",
    ["cici", "Cici", "Dola", "ciciai"],
)

# --- 华为小艺（盘古/ModelArts 企业云不收） ---
_on(
    WDL, SH_AI, "xiaoyi",
    "华为小艺（对话网页；lookup 打开官网。系统内置助手无独立安装包）",
    "AI",
    "https://xiaoyi.huawei.com/",
    ["xiaoyi", "小艺", "华为小艺", "Celia"],
)

# --- 阶跃星辰 跃问 ---
_on(
    WDL, SH_AI, "yuewen",
    "跃问（阶跃星辰对话网页；lookup 打开官网）",
    "AI",
    "https://stepchat.cn/",
    ["yuewen", "跃问", "阶跃", "阶跃星辰", "stepfun", "stepchat"],
)

# --- 零一万物（C 端已转企业门户） ---
_on(
    WDL, SH_AI, "lingyi",
    "零一万物（公司/产品门户；lookup 打开官网）",
    "AI",
    "https://www.lingyiwanwu.com/",
    ["lingyi", "零一万物", "01.ai", "01ai", "万知"],
)

# --- 商汤日日新 ---
_on(
    WDL, SH_AI, "sensenova",
    "商汤日日新 / 商量（大模型门户；lookup 打开官网）",
    "AI",
    "https://www.sensenova.cn/",
    ["sensenova", "日日新", "商量", "商汤", "SenseChat"],
)

# --- Meta AI ---
_on(
    WDL, SH_AI, "meta_ai",
    "Meta AI（对话网页；lookup 打开官网）",
    "AI",
    "https://www.meta.ai/",
    ["meta ai", "Meta AI", "meta.ai", "Llama"],
)

# --- Amazon Q 产品页（CLI 见 amazon_q_cli） ---
_on(
    WDL, SH_AI, "amazon_q",
    "Amazon Q（AWS 编程/云助手产品页；lookup 打开官网。CLI 见 amazon_q_cli）",
    "AI",
    "https://aws.amazon.com/q/",
    ["amazon q", "Amazon Q", "amazonq"],
)

# --- 360 智脑（只要 AI 网页，不要安全卫士） ---
_on(
    WDL, SH_AI, "ai360",
    "360 智脑（对话网页；lookup 打开官网。不是 360 安全卫士）",
    "AI",
    "https://ai.360.com/",
    ["360智脑", "智脑", "ai360", "360 AI"],
)

# --- Android：头部对话（Play 已核实或官网） ---
_madd("android", SH_AI, [_page(
    "doubao_android",
    "豆包 Android（lookup 打开官网）",
    "AI", "https://www.doubao.com/",
    ["doubao", "豆包", "doubao ai"],
)])
_madd("android", SH_AI, [_page(
    "qwen_android",
    "千问 Android（lookup 打开官网）",
    "AI", "https://www.qianwen.com/",
    ["qwen", "Qwen", "千问", "通义千问", "tongyi", "qianwen"],
)])
_madd("android", SH_AI, [_page(
    "kimi_android",
    "Kimi Android（lookup 打开商店页）",
    "AI", "https://play.google.com/store/apps/details?id=com.moonshot.kimichat",
    ["kimi", "Kimi", "月之暗面"],
)])
_madd("android", SH_AI, [_page(
    "deepseek_android",
    "DeepSeek Android（lookup 打开官网）",
    "AI", "https://chat.deepseek.com/",
    ["deepseek", "DeepSeek", "深度求索"],
)])
_madd("android", SH_AI, [_page(
    "yuanbao_android",
    "腾讯元宝 Android（lookup 打开官网）",
    "AI", "https://yuanbao.tencent.com/",
    ["yuanbao", "元宝", "腾讯元宝"],
)])
_madd("android", SH_AI, [_page(
    "claude_android",
    "Claude Android（lookup 打开商店页）",
    "AI", "https://play.google.com/store/apps/details?id=com.anthropic.claude",
    ["claude", "Claude", "anthropic"],
)])
_madd("android", SH_AI, [_page(
    "spark_android",
    "讯飞星火 Android（lookup 打开官网）",
    "AI", "https://xinghuo.xfyun.cn/",
    ["spark", "星火", "讯飞星火", "xinghuo"],
)])
_madd("android", SH_AI, [_page(
    "zhipu_android",
    "智谱清言 Android（lookup 打开官网）",
    "AI", "https://chatglm.cn/",
    ["zhipu", "智谱", "清言", "智谱清言", "chatglm"],
)])

# --- iOS：官方 App Store（chatgpt_ios 已在 99-占位） ---
def store(app_id: int) -> str:
    return "https://apps.apple.com/app/id%d" % app_id


_madd("ios", SH_AI, [_ios(
    "claude_ios", "Claude", "AI", store(6473753684),
    ["claude", "Claude", "anthropic"],
)])
_madd("ios", SH_AI, [_ios(
    "doubao_ios", "豆包", "AI", store(6459478672),
    ["doubao", "豆包", "doubao ai"],
)])
_madd("ios", SH_AI, [_ios(
    "yuanbao_ios", "腾讯元宝", "AI", store(6480446430),
    ["yuanbao", "元宝", "腾讯元宝"],
)])
_madd("ios", SH_AI, [_ios(
    "kimi_ios", "Kimi", "AI", store(6474233312),
    ["kimi", "Kimi", "月之暗面"],
)])
_madd("ios", SH_AI, [_ios(
    "deepseek_ios", "DeepSeek", "AI", store(6737597349),
    ["deepseek", "DeepSeek", "深度求索"],
)])
_madd("ios", SH_AI, [_ios(
    "qwen_ios", "千问", "AI", store(6466733523),
    ["qwen", "Qwen", "千问", "通义千问", "tongyi", "qianwen"],
)])
_madd("ios", SH_AI, [_ios(
    "spark_ios", "讯飞星火", "AI", store(6449919551),
    ["spark", "星火", "讯飞星火", "xinghuo"],
)])
_madd("ios", SH_AI, [_ios(
    "zhipu_ios", "智谱清言", "AI", store(6450893458),
    ["zhipu", "智谱", "清言", "智谱清言", "chatglm"],
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
