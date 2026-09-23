#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""apps-mobile batch9：iOS 装机必备 → App Store / 官网占位（lookup 打开页面）。"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOBILE = os.path.join(ROOT, "apps-mobile")
BATCH: dict[str, list] = {}


def _add(shard: str, apps: list):
    BATCH.setdefault(shard, []).extend(apps)


def store(app_id: int) -> str:
    return "https://apps.apple.com/app/id%d" % app_id


def _page(shard, aid, 简介, 分类, url, aliases):
    _add(shard, [{
        "id": aid,
        "简介": 简介,
        "分类": 分类,
        "aliases": list(aliases),
        "enabled": False,
        "open_page_only": True,
        "open_page_url": url,
        "releases_url": url,
        "url_hint": " ".join(aliases),
        "run_installer": False,
        "kill_before_install": False,
        "windows_installer": False,
        "process_name": "",
    }])


def _ios(shard, aid, name, 分类, url, aliases):
    _page(
        shard, aid,
        "%s（iOS · App Store；lookup 打开商店页，勿启用 auto_update）" % name,
        分类, url, aliases,
    )


# --- 通讯 ---
C20, S20 = "网络与通讯", "20-网络与通讯.json"
_ios(S20, "wechat_ios", "微信", C20, store(414478124), ["wechat", "weixin", "微信"])
_ios(S20, "qq_ios", "QQ", C20, store(444934666), ["qq", "QQ", "手机QQ"])
_ios(S20, "wecom_ios", "企业微信", C20, store(1029197278), ["wecom", "企业微信", "wework"])
_ios(S20, "feishu_ios", "飞书", C20, store(1451810416), ["feishu", "飞书", "lark"])
_ios(S20, "dingtalk_ios", "钉钉", C20, store(930368808), ["dingtalk", "钉钉"])
_ios(S20, "instagram_ios", "Instagram", C20, store(389801252), ["instagram", "ins", "ig", "Instagram"])
_ios(S20, "facebook_ios", "Facebook", C20, store(284882215), ["facebook", "fb", "脸书"])
_ios(S20, "messenger_ios", "Messenger", C20, store(454638411), ["messenger", "facebook messenger"])
_ios(S20, "whatsapp_ios", "WhatsApp", C20, store(310633997), ["whatsapp", "WhatsApp"])
_ios(S20, "weibo_ios", "微博", C20, store(350962117), ["weibo", "微博"])
_ios(S20, "reddit_ios", "Reddit", C20, store(1064216828), ["reddit", "Reddit"])
_ios(S20, "snapchat_ios", "Snapchat", C20, store(447188370), ["snapchat", "Snapchat"])
_ios(S20, "skype_ios", "Skype", C20, store(304878510), ["skype", "Skype"])
_ios(S20, "line_ios", "LINE", C20, store(443904275), ["line", "LINE"])
_ios(S20, "twitter_ios", "X / Twitter", C20, store(333903271), ["twitter", "x.com", "推特", "X"])
_ios(S20, "threads_ios", "Threads", C20, store(6446901002), ["threads", "Threads"])
_ios(S20, "discord_ios", "Discord", C20, store(985746746), ["discord", "Discord"])

# --- 浏览器 ---
C10, S10 = "浏览器", "10-浏览器.json"
_ios(S10, "chrome_ios", "Google Chrome", C10, store(535886823), ["chrome", "谷歌浏览器", "Chrome"])
_ios(S10, "edge_ios", "Microsoft Edge", C10, store(1288723196), ["edge", "Edge", "微软浏览器"])
_ios(S10, "opera_ios", "Opera", C10, store(1411861975), ["opera", "Opera"])

# --- 音视频 ---
C22, S22 = "音视频", "22-音视频.json"
_ios(S22, "youtube_ios", "YouTube", C22, store(544007664), ["youtube", "YouTube", "油管"])
_ios(S22, "bilibili_ios", "哔哩哔哩", C22, store(736536022), ["bilibili", "b站", "哔哩哔哩"])
_ios(S22, "netflix_ios", "Netflix", C22, store(363590051), ["netflix", "Netflix"])
_ios(S22, "douyin_ios", "抖音", C22, store(1142110895), ["douyin", "抖音", "tiktok中国"])
_ios(S22, "tiktok_ios", "TikTok", C22, store(835599320), ["tiktok", "TikTok"])
_ios(S22, "kuaishou_ios", "快手", C22, store(440948110), ["kuaishou", "快手"])
_ios(S22, "youku_ios", "优酷", C22, store(336141440), ["youku", "优酷"])
_ios(S22, "iqiyi_ios", "爱奇艺", C22, store(393280425), ["iqiyi", "爱奇艺"])
_ios(S22, "capcut_ios", "剪映 / CapCut", C22, store(1500855883), ["capcut", "jianying", "剪映"])

# --- 音乐 ---
C08, S08 = "多媒体", "08-多媒体.json"
_ios(S08, "netease_cloud_ios", "网易云音乐", C08, store(590338362), ["netease", "网易云", "网易云音乐"])
_ios(S08, "qqmusic_ios", "QQ 音乐", C08, store(414603431), ["qqmusic", "QQ音乐"])

# --- 社区 ---
C03, S03 = "写作", "03-写作.json"
_ios(S03, "xiaohongshu_ios", "小红书", C03, store(741292507), ["xiaohongshu", "小红书", "rednote", "xhs"])
_ios(S03, "zhihu_ios", "知乎", C03, store(432274380), ["zhihu", "知乎"])

# --- 网盘 ---
C07, S07 = "备份", "07-备份.json"
_ios(S07, "baidunetdisk_ios", "百度网盘", C07, store(547166701), ["baidunetdisk", "百度网盘", "百度云"])
_ios(S07, "aliyundrive_ios", "阿里云盘", C07, store(1500032156), ["aliyundrive", "阿里云盘", "alipan"])
_ios(S07, "googledrive_ios", "Google Drive", C07, store(507874739), ["google drive", "googledrive", "谷歌云盘"])
_ios(S07, "onedrive_ios", "OneDrive", C07, store(477537958), ["onedrive", "OneDrive"])
_ios(S07, "dropbox_ios", "Dropbox", C07, store(327630330), ["dropbox", "Dropbox"])

# --- 办公 ---
C04, S04 = "办公", "04-办公.json"
_ios(S04, "wps_ios", "WPS 办公", C04, store(599852710), ["wps", "WPS", "金山办公"])
_ios(S04, "microsoft_365_ios", "Microsoft 365", C04, store(541164951), ["office", "microsoft 365", "Office"])
_ios(S04, "google_docs_ios", "Google 文档", C04, store(842842640), ["google docs", "谷歌文档"])
_ios(S04, "adobe_reader_ios", "Adobe Acrobat Reader", C04, store(469337564), ["adobe reader", "acrobat", "PDF"])
_ios(S04, "canva_ios", "Canva", C04, store(897446215), ["canva", "Canva"])

# --- 输入法 ---
_ios("08-输入.json", "sogou_ios", "搜狗输入法", "输入", store(917890493),
     ["sogou", "搜狗", "搜狗输入法"])

# --- 远程 ---
C21, S21 = "远程与协作", "21-远程与协作.json"
_page(S21, "todesk_ios",
      "ToDesk（iOS；lookup 打开官网下载页，勿启用 auto_update）",
      C21, "https://www.todesk.com/download.html",
      ["todesk", "ToDesk"])
_ios(S21, "anydesk_ios", "AnyDesk", C21, store(1173237980), ["anydesk", "AnyDesk"])
_ios(S21, "teamviewer_ios", "TeamViewer", C21, store(692368163), ["teamviewer", "TeamViewer"])
_page(S21, "sunlogin_ios",
      "向日葵（iOS；lookup 打开官网下载页，勿启用 auto_update）",
      C21, "https://sunlogin.oray.com/download",
      ["sunlogin", "向日葵", "oray"])
_ios(S21, "zoom_ios", "Zoom", C21, store(546505307), ["zoom", "Zoom"])
_ios(S21, "teams_ios", "Microsoft Teams", C21, store(1113153706), ["teams", "Microsoft Teams"])
_ios(S21, "meet_ios", "Google Meet", C21, store(1099417390), ["google meet", "meet", "谷歌会议"])

# --- 下载 ---
_page("02-下载.json", "xunlei_ios",
      "迅雷（iOS；lookup 打开官网，勿启用 auto_update）",
      "下载", "https://www.xunlei.com/",
      ["xunlei", "thunder", "迅雷"])

# --- 金融 ---
_ios("27-金融与股票.json", "alipay_ios", "支付宝", "金融与股票", store(333206289),
     ["alipay", "支付宝"])
_ios("27-金融与股票.json", "paypal_ios", "PayPal", "金融与股票", store(283646709),
     ["paypal", "PayPal"])

# --- AI（chatgpt_ios 已在 99-占位） ---
_ios("01-AI.json", "gemini_ios", "Google Gemini", "AI", store(6477489729),
     ["gemini", "Gemini", "bard"])
_ios("01-AI.json", "copilot_ios", "Microsoft Copilot", "AI", store(6472538445),
     ["copilot", "Copilot"])

# --- 游戏 ---
_ios("14-游戏.json", "steam_ios", "Steam", "游戏", store(495890035),
     ["steam", "Steam"])
_ios("14-游戏.json", "taptap_ios", "TapTap", "游戏", store(1114540102),
     ["taptap", "TapTap"])

# --- 工具 ---
C11, S11 = "工具", "11-工具.json"
_ios(S11, "google_maps_ios", "Google 地图", C11, store(585027354),
     ["google maps", "谷歌地图", "maps"])
_ios(S11, "amap_ios", "高德地图", C11, store(461703208), ["amap", "高德", "高德地图"])
_ios(S11, "baidu_map_ios", "百度地图", C11, store(452186370), ["baidu map", "百度地图"])
_ios(S11, "gmail_ios", "Gmail", C11, store(422689480), ["gmail", "Gmail"])
_ios(S11, "google_keep_ios", "Google Keep", C11, store(1020351700), ["keep", "google keep"])
_ios(S11, "google_photos_ios", "Google 相册", C11, store(962194608),
     ["google photos", "谷歌相册"])
_ios(S11, "taobao_ios", "淘宝", C11, store(387682726), ["taobao", "淘宝"])
_ios(S11, "jd_ios", "京东", C11, store(414245413), ["jd", "京东", "jingdong"])
_ios(S11, "pinduoduo_ios", "拼多多", C11, store(1044283059), ["pinduoduo", "拼多多", "pdd"])
_ios(S11, "meituan_ios", "美团", C11, store(423084029), ["meituan", "美团"])
_ios(S11, "didi_ios", "滴滴出行", C11, store(554499054), ["didi", "滴滴"])
_ios(S11, "amazon_ios", "Amazon", C11, store(297606951), ["amazon", "亚马逊"])


def _load_existing() -> set[str]:
    ids: set[str] = set()
    d = os.path.join(MOBILE, "ios")
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


def main():
    dry = "--dry-run" in sys.argv
    seen = _load_existing()
    total = 0
    skipped = 0
    for shard, apps in sorted(BATCH.items()):
        path = os.path.join(MOBILE, "ios", shard)
        existing = json.load(open(path, encoding="utf-8")) if os.path.isfile(path) else []
        file_ids = {(a.get("id") or "").strip() for a in existing if isinstance(a, dict)}
        for app in apps:
            aid = (app.get("id") or "").strip()
            if aid in seen or aid in file_ids:
                skipped += 1
                continue
            existing.append(app)
            seen.add(aid)
            file_ids.add(aid)
            total += 1
        if not dry:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)
                f.write("\n")
            print("Wrote", path, "count", len(existing))
    print(f"{'dry-run' if dry else 'done'}: added {total} skip {skipped}")


if __name__ == "__main__":
    main()
