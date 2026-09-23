#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Batch28：再搜一轮同类主流 AI（对话/生图视频/会议/代码/工作流/知识/搜索/推理台）→ open_page_only。"""
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
SH_AI = "01-AI.json"
SH_REMOTE = "21-远程与协作.json"
SH_NOTE = "15-笔记.json"
SH_EFF = "13-效率.json"
SH_IM = "20-网络与通讯.json"

# --- 对话 ---
_on(WDL, SH_AI, "gemini",
    "Google Gemini（对话网页；lookup 打开官网。CLI 见 gemini_cli）", "AI",
    "https://gemini.google.com/",
    ["gemini", "Gemini", "bard", "双子座", "Google Gemini"])
_on(WDL, SH_AI, "grok",
    "Grok（xAI 对话网页；lookup 打开官网）", "AI",
    "https://grok.com/",
    ["grok", "Grok", "xAI", "grok.com"])
_on(WDL, SH_AI, "poe",
    "Poe（Quora 多模型对话网页；lookup 打开官网）", "AI",
    "https://poe.com/",
    ["poe", "Poe", "poe.com"])
_on(WDL, SH_AI, "qwen",
    "千问 / 通义千问（阿里对话网页；lookup 打开官网。CLI 见 qwen_code）", "AI",
    "https://www.qianwen.com/",
    ["qwen", "Qwen", "千问", "通义千问", "tongyi", "qianwen"])
_on(WDL, SH_AI, "wenxin",
    "文心（百度对话网页，原「文心一言」；lookup 打开官网）", "AI",
    "https://wenxin.baidu.com/",
    ["wenxin", "文心", "文心一言", "文心一格", "yiyan", "ernie"])
_on(WDL, SH_AI, "spark",
    "讯飞星火（对话网页；lookup 打开官网）", "AI",
    "https://xinghuo.xfyun.cn/",
    ["spark", "星火", "讯飞星火", "xinghuo", "讯飞"])
_on(WDL, SH_AI, "zhipu",
    "智谱清言 / ChatGLM（对话网页；lookup 打开官网）", "AI",
    "https://chatglm.cn/",
    ["zhipu", "智谱", "清言", "智谱清言", "chatglm", "ChatGLM"])
_on(WDL, SH_AI, "minimax",
    "MiniMax Agent（海螺对话网页；lookup 打开官网。视频见 hailuo_video）", "AI",
    "https://agent.minimaxi.com/",
    ["minimax", "MiniMax", "海螺", "海螺AI", "海螺对话"])
_on(WDL, SH_AI, "baichuan",
    "百川 / 百小应（对话网页；lookup 打开官网）", "AI",
    "https://yi.baichuan-ai.com/",
    ["baichuan", "百川", "百小应", "百川智能"])
_on(WDL, SH_AI, "hunyuan",
    "腾讯混元（对话网页；lookup 打开官网。C 端助手见 yuanbao）", "AI",
    "https://hunyuan.tencent.com/",
    ["hunyuan", "混元", "腾讯混元"])

# --- 图像 / 视频 ---
_on(WDL, SH_AI, "runway",
    "Runway（AI 视频生成网页；lookup 打开官网）", "AI",
    "https://runway.com/",
    ["runway", "Runway", "runwayml"])
_on(WDL, SH_AI, "pika_ai",
    "Pika（AI 视频生成网页；lookup 打开官网。与 macOS 取色工具 pika 区分）", "AI",
    "https://pika.art/",
    ["pika", "Pika", "pika.art", "Pika AI"])
_on(WDL, SH_AI, "luma",
    "Luma Dream Machine（AI 视频生成网页；lookup 打开官网）", "AI",
    "https://lumalabs.ai/",
    ["luma", "Luma", "Dream Machine", "lumalabs"])
_on(WDL, SH_AI, "leonardo",
    "Leonardo（AI 生图网页；lookup 打开官网）", "AI",
    "https://leonardo.ai/",
    ["leonardo", "Leonardo", "Leonardo AI"])
_on(WDL, SH_AI, "ideogram",
    "Ideogram（AI 生图 / 文字排版网页；lookup 打开官网）", "AI",
    "https://ideogram.ai/",
    ["ideogram", "Ideogram"])
_on(WDL, SH_AI, "flux",
    "FLUX / Black Forest Labs（生图官网；lookup 打开。本地工作流见 comfyui）", "AI",
    "https://bfl.ai/",
    ["flux", "FLUX", "Black Forest Labs", "bfl", "flux.ai"])
_on(WDL, SH_AI, "wanxiang",
    "通义万相（阿里图像/视频生成网页；lookup 打开官网）", "AI",
    "https://tongyi.aliyun.com/wan/",
    ["wanxiang", "万相", "通义万相", "wan"])
_on(WDL, SH_AI, "vidu",
    "Vidu（生数科技视频生成网页；lookup 打开官网）", "AI",
    "https://www.vidu.com/",
    ["vidu", "Vidu", "生数", "vidu.cn"])
_on(WDL, SH_AI, "hailuo_video",
    "海螺视频（MiniMax 视频生成网页；lookup 打开官网。对话见 minimax）", "AI",
    "https://hailuoai.com/",
    ["hailuo", "海螺视频", "Hailuo", "hailuoai"])
_on(WDL, SH_AI, "comfyui_desktop",
    "Comfy Desktop（官方桌面端下载页；lookup 打开。便携包见 comfyui）", "AI",
    "https://comfy.org/",
    ["comfy desktop", "Comfy Desktop", "ComfyUI Desktop", "comfy.org"])

# --- 会议转写 ---
_on(WDL, SH_REMOTE, "otter",
    "Otter（会议转写网页；lookup 打开官网）", "远程与协作",
    "https://otter.ai/",
    ["otter", "Otter", "otter.ai"])
_on(WDL, SH_REMOTE, "fireflies",
    "Fireflies（会议转写网页；lookup 打开官网）", "远程与协作",
    "https://fireflies.ai/",
    ["fireflies", "Fireflies"])
_on(WDL, SH_REMOTE, "tingwu",
    "通义听悟（会议/音视频转写网页；lookup 打开官网）", "远程与协作",
    "https://tingwu.aliyun.com/",
    ["tingwu", "听悟", "通义听悟"])
_on(WDL, SH_REMOTE, "notta",
    "Notta（会议转写网页；lookup 打开官网）", "远程与协作",
    "https://www.notta.ai/",
    ["notta", "Notta"])

# --- 代码 ---
_on(WDL, SH_AI, "tabnine",
    "Tabnine（AI 代码补全产品页；lookup 打开官网）", "AI",
    "https://www.tabnine.com/",
    ["tabnine", "Tabnine"])
_on(WDL, SH_AI, "gemini_code_assist",
    "Gemini Code Assist（Google 代码助手产品页；lookup 打开官网。CLI 见 gemini_cli）", "AI",
    "https://codeassist.google/",
    ["gemini code assist", "Gemini Code Assist", "code assist", "duet ai"])

# --- 工作流 ---
_on(WDL, SH_EFF, "n8n",
    "n8n（开源自动化工作流；lookup 打开官网，自托管用 Docker）", "效率",
    "https://n8n.io/",
    ["n8n", "n8n.io"])
_on(WDL, SH_EFF, "activepieces",
    "Activepieces（开源自动化工作流；lookup 打开官网）", "效率",
    "https://www.activepieces.com/",
    ["activepieces", "Activepieces"])

# --- 知识 ---
_on(WDL, SH_NOTE, "yuque",
    "语雀（知识库网页；lookup 打开官网）", "笔记",
    "https://www.yuque.com/",
    ["yuque", "语雀"])
_on(WDL, SH_NOTE, "feishu_wiki",
    "飞书知识库（产品页；lookup 打开官网。客户端见 feishu）", "笔记",
    "https://www.feishu.cn/product/wiki",
    ["feishu wiki", "飞书知识库", "知识库", "lark wiki"])

# --- 搜索 ---
_on(WDL, SH_AI, "you_com",
    "You.com（AI 搜索网页；lookup 打开官网）", "AI",
    "https://you.com/",
    ["you.com", "You.com", "youcom"])
_on(WDL, SH_AI, "phind",
    "Phind（开发者 AI 搜索网页；lookup 打开官网）", "AI",
    "https://www.phind.com/",
    ["phind", "Phind"])
_on(WDL, SH_AI, "tiangong",
    "天工（昆仑万维 AI 搜索/助手网页；lookup 打开官网）", "AI",
    "https://www.tiangong.cn/",
    ["tiangong", "天工", "天工AI", "skywork"])
_on(WDL, SH_AI, "genspark",
    "Genspark（AI 工作区 / 搜索网页；lookup 打开官网）", "AI",
    "https://www.genspark.ai/",
    ["genspark", "Genspark"])
_on(WDL, SH_AI, "felo",
    "Felo（多语言 AI 搜索网页；lookup 打开官网）", "AI",
    "https://felo.ai/",
    ["felo", "Felo", "felo.ai"])

# --- 模型站 / 推理台 ---
_on(WDL, SH_AI, "huggingface",
    "Hugging Face（模型/Spaces 网页；lookup 打开官网）", "AI",
    "https://huggingface.co/",
    ["huggingface", "Hugging Face", "hf", "spaces", "Hugging Face Spaces"])
_on(WDL, SH_AI, "groq",
    "Groq 控制台（高速推理网页；lookup 打开官网）", "AI",
    "https://console.groq.com/",
    ["groq", "Groq", "groq console"])
_on(WDL, SH_AI, "openrouter",
    "OpenRouter（多模型 API 路由网页；lookup 打开官网）", "AI",
    "https://openrouter.ai/",
    ["openrouter", "OpenRouter"])
_on(WDL, SH_AI, "siliconflow",
    "硅基流动（模型推理控制台；lookup 打开官网）", "AI",
    "https://cloud.siliconflow.cn/",
    ["siliconflow", "硅基流动", "硅基", "silicon flow"])


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


def _patch_feishu_aliases(dry: bool) -> int:
    extra = ["飞书知识库", "知识库", "wiki", "lark wiki"]
    n = 0
    for plat in WDL:
        path = os.path.join(APPS, plat, SH_IM)
        if not os.path.isfile(path):
            continue
        data = json.load(open(path, encoding="utf-8"))
        changed = False
        for item in data:
            if not isinstance(item, dict) or item.get("id") != "feishu":
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
        if changed:
            n += 1
            if not dry:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    f.write("\n")
                print(f"Patched feishu aliases: {path}")
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
                print(f"skip {plat}/{aid}")
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
    p = _patch_feishu_aliases(dry)
    print(f"{'dry-run' if dry else 'done'}: +{a} skip {s} feishu_patch {p}")


if __name__ == "__main__":
    main()
