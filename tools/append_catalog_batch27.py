#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Batch27：基础必用 / 进阶选配 AI 清单 → 缺的做成 open_page_only（lookup 打开官网）。"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS = os.path.join(ROOT, "apps")
BATCH: dict[tuple[str, str], list] = {}


def _add(plat: str, shard: str, apps: list):
    BATCH.setdefault((plat, shard), []).extend(apps)


def _page(aid, 简介, 分类, url, aliases):
    return {
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


def _on(plats, shard, aid, 简介, 分类, url, aliases, urls=None):
    urls = urls or {}
    for plat in plats:
        _add(plat, shard, [_page(aid, 简介, 分类, urls.get(plat, url), aliases)])


WDL = ("windows", "darwin", "linux")
WD = ("windows", "darwin")

SH_AI = "01-AI.json"
SH_AV = "22-音视频.json"
SH_REMOTE = "21-远程与协作.json"
SH_EFF = "13-效率.json"
SH_NOTE = "15-笔记.json"

# --- 基础对话（网页；darwin 已有 chatgpt，merge 会跳过）---
_on(WDL, SH_AI, "chatgpt",
    "ChatGPT（OpenAI 对话；lookup 打开官网，不自动下载客户端）", "AI",
    "https://chatgpt.com/",
    ["chatgpt", "ChatGPT", "openai", "GPT"],
    urls={"windows": "https://chatgpt.com/download/", "darwin": "https://chatgpt.com/download/"})
_on(WDL, SH_AI, "claude",
    "Claude（Anthropic 对话网页；lookup 打开官网。CLI 见 claude_code）", "AI",
    "https://claude.ai/",
    ["claude", "Claude", "anthropic", "克劳德"])
_on(WDL, SH_AI, "deepseek",
    "DeepSeek（深度求索对话网页；lookup 打开官网。CLI 见 deepseek_cli）", "AI",
    "https://chat.deepseek.com/",
    ["deepseek", "DeepSeek", "深度求索"])
_on(WDL, SH_AI, "yuanbao",
    "腾讯元宝（对话网页；lookup 打开官网）", "AI",
    "https://yuanbao.tencent.com/",
    ["yuanbao", "元宝", "腾讯元宝"])
_on(WDL, SH_AI, "kimi",
    "Kimi（月之暗面对话网页；lookup 打开官网。CLI 见 kimi_cli）", "AI",
    "https://www.kimi.com/",
    ["kimi", "Kimi", "月之暗面", "kimi.ai"])
_on(WDL, SH_AI, "doubao",
    "豆包（字节对话网页；lookup 打开官网）", "AI",
    "https://www.doubao.com/",
    ["doubao", "豆包", "doubao ai"])

# --- 图像 / 视频生成 ---
_on(WDL, SH_AI, "jimeng",
    "即梦 AI（字节图像/视频生成网页；lookup 打开官网）", "AI",
    "https://jimeng.jianying.com/",
    ["jimeng", "即梦", "即梦AI", "即梦 AI"])
_on(WDL, SH_AI, "kling",
    "可灵（快手图像/视频生成网页；lookup 打开官网）", "AI",
    "https://klingai.kuaishou.com/",
    ["kling", "可灵", "可灵AI", "klingai"])
_on(WDL, SH_AI, "midjourney",
    "Midjourney（图像生成网页；lookup 打开官网）", "AI",
    "https://www.midjourney.com/",
    ["midjourney", "Midjourney", "MJ"])
_on(("linux",), SH_AV, "capcut",
    "剪映 / CapCut（字节剪辑；官网分发，lookup 打开下载页）", "音视频",
    "https://www.capcut.cn/",
    ["capcut", "jianying", "剪映", "剪映专业版"])

# --- 会议转写 ---
_on(WDL, SH_REMOTE, "iflyrec",
    "讯飞听见（会议/录音转写网页；lookup 打开官网）", "远程与协作",
    "https://www.iflyrec.com/",
    ["iflyrec", "讯飞听见", "听见", "讯飞转写"])
_on(WDL, SH_REMOTE, "feishu_minutes",
    "飞书妙记（会议转写网页；lookup 打开官网。客户端见 feishu）", "远程与协作",
    "https://www.feishu.cn/product/minutes",
    ["feishu minutes", "飞书妙记", "妙记", "lark minutes"])

# --- 代码助手（网页入口；Cursor/Windsurf/Zed 已有安装包条目）---
_on(WDL, SH_AI, "github_copilot",
    "GitHub Copilot（官方产品页；lookup 打开官网。CLI 见 github_copilot_cli）", "AI",
    "https://github.com/features/copilot",
    ["github copilot", "GitHub Copilot", "copilot"])

# --- 工作流 ---
_on(WDL, SH_AI, "coze",
    "扣子 Coze（字节智能体/工作流网页；lookup 打开官网）", "AI",
    "https://www.coze.cn/",
    ["coze", "扣子", "扣子 Coze", "coze.cn"])
_on(WDL, SH_AI, "dify",
    "Dify（开源 LLM 应用/工作流平台；lookup 打开官网，自托管用 Docker）", "AI",
    "https://dify.ai/",
    ["dify", "Dify"])
_on(WDL, SH_EFF, "zapier",
    "Zapier（自动化工作流网页；lookup 打开官网）", "效率",
    "https://zapier.com/",
    ["zapier", "Zapier"])
_on(WDL, SH_EFF, "make",
    "Make（原 Integromat；自动化工作流网页；lookup 打开官网）", "效率",
    "https://www.make.com/",
    ["make", "Make", "integromat", "Integromat"])
_on(WDL, SH_EFF, "jijyun",
    "集简云（国内自动化集成网页；lookup 打开官网）", "效率",
    "https://www.jijyun.cn/",
    ["jijyun", "集简云", "jijian"])

# --- 知识库 ---
_on(WDL, SH_NOTE, "cubox",
    "Cubox（稍后读 / 知识库网页；lookup 打开官网）", "笔记",
    "https://cubox.cc/",
    ["cubox", "Cubox"])
_on(WDL, SH_AI, "fastgpt",
    "FastGPT（开源知识库问答；lookup 打开官网，自托管用 Docker）", "AI",
    "https://fastgpt.in/",
    ["fastgpt", "FastGPT"])

# --- 搜索 ---
_on(WDL, SH_AI, "metaso",
    "秘塔 AI 搜索（网页；lookup 打开官网）", "AI",
    "https://metaso.cn/",
    ["metaso", "秘塔", "秘塔AI", "秘塔搜索"])
_on(WDL, SH_AI, "perplexity",
    "Perplexity（AI 搜索网页；lookup 打开官网）", "AI",
    "https://www.perplexity.ai/",
    ["perplexity", "Perplexity"])

# --- 云端生图 ---
_on(WDL, SH_AI, "rundiffusion",
    "RunDiffusion（云端生图网页；lookup 打开官网）", "AI",
    "https://www.rundiffusion.com/",
    ["rundiffusion", "RunDiffusion"])
_on(WDL, SH_AI, "runcomfy",
    "RunComfy（云端 ComfyUI 网页；lookup 打开官网）", "AI",
    "https://www.runcomfy.com/",
    ["runcomfy", "RunComfy"])


def _load_existing(plat: str) -> set[str]:
    ids: set[str] = set()
    d = os.path.join(APPS, plat)
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


def _patch_notion_aliases(dry: bool) -> int:
    extra = ["Notion AI", "notion ai"]
    n = 0
    for plat in WDL:
        path = os.path.join(APPS, plat, SH_NOTE)
        if not os.path.isfile(path):
            continue
        data = json.load(open(path, encoding="utf-8"))
        changed = False
        for item in data:
            if not isinstance(item, dict) or item.get("id") != "notion":
                continue
            aliases = list(item.get("aliases") or [])
            for a in extra:
                if a not in aliases:
                    aliases.append(a)
                    changed = True
            item["aliases"] = aliases
            hint = item.get("url_hint") or ""
            for a in extra:
                if a.lower() not in hint.lower():
                    hint = (hint + " " + a).strip()
                    changed = True
            item["url_hint"] = hint
            intro = item.get("简介") or ""
            if "Notion AI" not in intro:
                item["简介"] = intro.replace(
                    "Notion 桌面版（官网分发，lookup 打开下载页）",
                    "Notion / Notion AI（官网分发，lookup 打开下载页）",
                )
                changed = True
        if changed:
            n += 1
            if not dry:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    f.write("\n")
                print(f"Patched notion aliases: {path}")
    return n


def _merge(dry: bool) -> tuple[int, int]:
    added = skipped = 0
    plat_ids: dict[str, set[str]] = {}
    for (plat, shard), apps in sorted(BATCH.items()):
        path = os.path.join(APPS, plat, shard)
        data = json.load(open(path, encoding="utf-8")) if os.path.isfile(path) else []
        if plat not in plat_ids:
            plat_ids[plat] = _load_existing(plat)
        seen = plat_ids[plat]
        file_ids = {(a.get("id") or "").strip() for a in data if isinstance(a, dict)}
        for app in apps:
            aid = (app.get("id") or "").strip()
            if aid in seen or aid in file_ids:
                skipped += 1
                continue
            data.append(app)
            seen.add(aid)
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
    p = _patch_notion_aliases(dry)
    print(f"{'dry-run' if dry else 'done'}: +{a} skip {s} notion_patch {p}")


if __name__ == "__main__":
    main()
