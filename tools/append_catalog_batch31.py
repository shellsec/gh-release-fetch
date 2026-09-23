#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Batch31：国内/国际大厂常用官方客户端（open_page_only，不硬编直链）。"""
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
WD = ("windows", "darwin")

SH_AI = "01-AI.json"
SH_WRITE = "03-写作.json"
SH_OFF = "04-办公.json"
SH_DESIGN = "05-办公与设计.json"
SH_BACKUP = "07-备份.json"
SH_MEDIA = "08-多媒体.json"
SH_TOOL = "11-工具.json"
SH_NOTE = "15-笔记.json"
SH_SYS = "16-系统.json"
SH_NET = "18-网络.json"
SH_IM = "20-网络与通讯.json"
SH_REMOTE = "21-远程与协作.json"
SH_AV = "22-音视频.json"
SH_FIN = "27-金融与股票.json"
SH_BROWSER = "10-浏览器.json"
SH_IME = "08-输入.json"

# --- 阿里：夸克（浏览器/网盘门户；注明广告风险） ---
_on(
    WD, SH_NET, "quark",
    "夸克（阿里浏览器/网盘门户；官网分发，lookup 打开下载页。含推广与会员引导，请自行甄别）",
    "网络",
    "https://www.quark.cn/",
    ["quark", "夸克", "夸克浏览器", "夸克网盘", "阿里"],
)

# --- 百度：输入法 ---
_on(
    WD, SH_SYS, "baidu_ime",
    "百度输入法（官网分发，lookup 打开下载页）",
    "系统",
    "https://shurufa.baidu.com/",
    ["baidu_ime", "百度输入法", "百度拼音", "百度"],
)

# --- 华为：电脑管家（仅 Windows / 华为机型） ---
_on(
    ("windows",), SH_SYS, "huawei_pc_manager",
    "华为电脑管家（华为 Windows 电脑官方；lookup 打开下载页。仅华为机型）",
    "系统",
    "https://consumer.huawei.com/cn/support/pc-manager/",
    ["huawei_pc_manager", "华为电脑管家", "华为", "PC Manager"],
)

# --- 华为云 WeLink ---
_on(
    WD, SH_IM, "welink",
    "华为云 WeLink（企业办公；官网分发，lookup 打开下载页）",
    "网络与通讯",
    "https://www.huaweicloud.com/product/welink-download.html",
    ["welink", "WeLink", "华为云WeLink", "华为"],
)

# --- 网易有道：词典 / 云笔记 ---
_on(
    WDL, SH_WRITE, "youdao_dict",
    "有道词典（网易有道；官网分发，lookup 打开下载页）",
    "写作",
    "https://cidian.youdao.com/",
    ["youdao_dict", "有道词典", "有道", "网易有道"],
)
_on(
    WDL, SH_NOTE, "youdao_note",
    "有道云笔记（网易有道；官网分发，lookup 打开下载页）",
    "笔记",
    "https://note.youdao.com/note-download/",
    ["youdao_note", "有道云笔记", "有道笔记", "网易有道"],
)

# --- 小米电脑管家（仅 Windows / 小米电脑） ---
_on(
    ("windows",), SH_SYS, "xiaomi_pc_manager",
    "小米电脑管家（小米/Redmi 电脑官方；lookup 打开官网帮助页。非小米电脑请勿用第三方破解包）",
    "系统",
    "https://pc.mi.com/pc-manager-help",
    ["xiaomi_pc_manager", "小米电脑管家", "小米", "红米电脑"],
)

# --- 微软 Outlook（M365/Teams/OneDrive 已有） ---
_on(
    WD, SH_IM, "outlook",
    "Microsoft Outlook（微软邮箱/日历；官网分发，lookup 打开下载页）",
    "网络与通讯",
    "https://www.microsoft.com/zh-cn/microsoft-365/outlook/email-and-calendar-software-microsoft-outlook",
    ["outlook", "Outlook", "微软邮箱", "微软"],
)

# --- Adobe Creative Cloud（仅官网，不收破解） ---
_on(
    WD, SH_DESIGN, "adobe_creative_cloud",
    "Adobe Creative Cloud（官方桌面应用；lookup 打开官网。不收录破解/绿色改包）",
    "办公与设计",
    "https://www.adobe.com/cn/creativecloud.html",
    ["adobe_creative_cloud", "Adobe", "Creative Cloud", "Adobe CC", "创意云"],
)

# --- B站 Windows（darwin 已有） ---
_on(
    ("windows",), SH_AV, "bilibili",
    "哔哩哔哩（官网分发，lookup 打开客户端下载页）",
    "音视频",
    "https://app.bilibili.com/",
    ["bilibili", "b站", "哔哩哔哩"],
)

# --- 抖音 Windows 电脑版（darwin 已有网页占位） ---
_on(
    ("windows",), SH_AV, "douyin",
    "抖音电脑版（字节；官网分发，lookup 打开下载页）",
    "音视频",
    "https://www.douyin.com/downloadpage/pc",
    ["douyin", "抖音", "抖音电脑版", "字节"],
)

# --- Google Drive for desktop Windows（darwin 已有） ---
_on(
    ("windows",), SH_BACKUP, "googledrive",
    "Google Drive for desktop（官网分发，lookup 打开下载页）",
    "备份",
    "https://www.google.com/drive/download/",
    ["google drive", "googledrive", "谷歌云盘", "Google"],
)

# --- 荣耀 / 联想电脑管家 ---
_on(
    ("windows",), SH_SYS, "honor_pc_manager",
    "荣耀电脑管家（荣耀官网；lookup 打开下载页。仅荣耀机型）",
    "系统",
    "https://www.honor.com/cn/tech/pc-manager/",
    ["honor_pc_manager", "荣耀电脑管家", "荣耀"],
)
_on(
    ("windows",), SH_SYS, "lenovo_pc_manager",
    "联想电脑管家（联想官网；lookup 打开下载页）",
    "系统",
    "https://guanjia.lenovo.com.cn/",
    ["lenovo_pc_manager", "联想电脑管家", "联想"],
)

# --- Apple：iTunes / iCloud（Windows；Mac 系统自带） ---
_on(
    ("windows",), SH_AV, "itunes",
    "iTunes（苹果官网 Windows 版；lookup 打开下载页。Mac 为系统自带/音乐 App）",
    "音视频",
    "https://www.apple.com.cn/itunes/",
    ["itunes", "iTunes", "苹果音乐", "Apple"],
)
_on(
    ("windows",), SH_BACKUP, "icloud",
    "iCloud for Windows（苹果；lookup 打开官网。Mac 为系统自带）",
    "备份",
    "https://www.icloud.com/",
    ["icloud", "iCloud", "苹果云盘", "Apple"],
)

# --- 支付宝 Windows 网页（darwin/移动已有） ---
_on(
    ("windows",), SH_FIN, "alipay",
    "支付宝（无官方 Windows 客户端；lookup 打开官网。客户端见 Android/iOS）",
    "金融与股票",
    "https://mobile.alipay.com/",
    ["alipay", "支付宝", "阿里"],
)

# --- 淘宝/京东/美团 Windows 各留 1 个官网（darwin/移动已有） ---
_on(
    ("windows",), SH_TOOL, "taobao",
    "淘宝（无官方 Windows 客户端；lookup 打开网页）",
    "工具",
    "https://www.taobao.com/",
    ["taobao", "淘宝", "阿里"],
)
_on(
    ("windows",), SH_TOOL, "jd",
    "京东（无官方 Windows 客户端；lookup 打开网页）",
    "工具",
    "https://www.jd.com/",
    ["jd", "京东", "jingdong"],
)
_on(
    ("windows",), SH_TOOL, "meituan",
    "美团（无官方 Windows 客户端；lookup 打开网页）",
    "工具",
    "https://www.meituan.com/",
    ["meituan", "美团"],
)

# --- 西瓜视频：低优先级，收 1 个官网网页 ---
_on(
    WD, SH_AV, "xigua",
    "西瓜视频（字节；网页，lookup 打开官网）",
    "音视频",
    "https://www.ixigua.com/",
    ["xigua", "西瓜视频", "西瓜", "字节"],
)

# --- Android ---
_madd("android", SH_BROWSER, [_page(
    "quark_android",
    "夸克 Android（阿里浏览器/网盘门户；lookup 打开官网。含推广与会员引导，请自行甄别）",
    "浏览器", "https://www.quark.cn/",
    ["quark", "夸克", "夸克浏览器", "夸克网盘", "阿里"],
)])
_madd("android", SH_IME, [_page(
    "baidu_ime_android",
    "百度输入法 Android（lookup 打开官网）",
    "输入", "https://shurufa.baidu.com/",
    ["baidu_ime", "百度输入法", "百度拼音", "百度"],
)])
_madd("android", SH_IM, [_page(
    "welink_android",
    "华为云 WeLink Android（lookup 打开官网下载页）",
    "网络与通讯", "https://www.huaweicloud.com/product/welink-download.html",
    ["welink", "WeLink", "华为云WeLink", "华为"],
)])
_madd("android", SH_WRITE, [_page(
    "youdao_dict_android",
    "有道词典 Android（lookup 打开官网）",
    "写作", "https://cidian.youdao.com/",
    ["youdao_dict", "有道词典", "有道", "网易有道"],
)])
_madd("android", SH_NOTE, [_page(
    "youdao_note_android",
    "有道云笔记 Android（lookup 打开官网）",
    "笔记", "https://note.youdao.com/note-download/",
    ["youdao_note", "有道云笔记", "有道笔记", "网易有道"],
)])
_madd("android", SH_IM, [_page(
    "outlook_android",
    "Microsoft Outlook Android（lookup 打开商店页）",
    "网络与通讯",
    "https://play.google.com/store/apps/details?id=com.microsoft.office.outlook",
    ["outlook", "Outlook", "微软邮箱", "微软"],
)])

# --- iOS ---
_madd("ios", SH_BROWSER, [_ios(
    "quark_ios", "夸克", "浏览器",
    "https://apps.apple.com/app/id1160172628",
    ["quark", "夸克", "夸克浏览器", "夸克网盘", "阿里"],
)])
_madd("ios", SH_IME, [_ios(
    "baidu_ime_ios", "百度输入法", "输入",
    "https://apps.apple.com/app/id916139408",
    ["baidu_ime", "百度输入法", "百度拼音", "百度"],
)])
_madd("ios", SH_IM, [_ios(
    "welink_ios", "华为云 WeLink", "网络与通讯",
    "https://apps.apple.com/app/id1382487847",
    ["welink", "WeLink", "华为云WeLink", "华为"],
)])
_madd("ios", SH_WRITE, [_ios(
    "youdao_dict_ios", "有道词典", "写作",
    "https://apps.apple.com/app/id353115739",
    ["youdao_dict", "有道词典", "有道", "网易有道"],
)])
_madd("ios", SH_NOTE, [_ios(
    "youdao_note_ios", "有道云笔记", "笔记",
    "https://apps.apple.com/app/id450748070",
    ["youdao_note", "有道云笔记", "有道笔记", "网易有道"],
)])
_madd("ios", SH_IM, [_ios(
    "outlook_ios", "Microsoft Outlook", "网络与通讯",
    "https://apps.apple.com/app/id951937596",
    ["outlook", "Outlook", "微软邮箱", "微软"],
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
