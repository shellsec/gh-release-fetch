#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""apps-mobile batch8：各分类装机必备（GitHub APK 或打开官网/商店）。"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOBILE = os.path.join(ROOT, "apps-mobile")
BATCH: dict[str, list] = {}


def _add(shard: str, apps: list):
    BATCH.setdefault(shard, []).extend(apps)


def _apk(**kw):
    d = {
        "enabled": False,
        "prefer_api_assets": True,
        "version_tag_as_on_github": True,
        "run_installer": False,
        "kill_before_install": False,
        "windows_installer": False,
        "process_name": "",
        "installer_extensions": [".apk"],
        "use_download_filename": True,
        "href_exclude_substrings": [
            "debug", ".aab", "test", "unsigned", "sources", ".json", ".txt",
        ],
    }
    d.update(kw)
    return d


def _page(shard, aid, 简介, 分类, url, aliases):
    _add(shard, [{
        "id": aid,
        "简介": 简介,
        "分类": 分类,
        "aliases": list(aliases),
        "enabled": False,
        "open_page_only": True,
        "open_page_url": url,
        "url_hint": " ".join(aliases),
        "run_installer": False,
        "kill_before_install": False,
        "windows_installer": False,
        "process_name": "",
    }])


def play(pkg):
    return "https://play.google.com/store/apps/details?id=" + pkg


# --- 通讯 ---
C20, S20 = "网络与通讯", "20-网络与通讯.json"
_page(S20, "wechat_android", "微信 Android（官方无 GitHub APK；lookup 打开下载页）", C20,
      "https://weixin.qq.com/", ["wechat", "weixin", "微信"])
_page(S20, "qq_android", "QQ Android（官方无 GitHub APK；lookup 打开下载页）", C20,
      "https://im.qq.com/mobileqq/", ["qq", "QQ", "手机QQ"])
_page(S20, "weibo", "微博 Android（lookup 打开商店页）", C20,
      play("com.sina.weibo"), ["weibo", "微博"])
_page(S20, "dingtalk_android", "钉钉 Android（lookup 打开官网下载页）", C20,
      "https://www.dingtalk.com/download", ["dingtalk", "钉钉"])
_page(S20, "wecom_android", "企业微信 Android（lookup 打开官网下载页）", C20,
      "https://work.weixin.qq.com/", ["wecom", "企业微信", "wework"])
_page(S20, "feishu_android", "飞书 Android（lookup 打开官网下载页）", C20,
      "https://www.feishu.cn/download", ["feishu", "飞书", "lark"])
_page(S20, "reddit", "Reddit 官方 Android（lookup 打开商店页）", C20,
      play("com.reddit.frontpage"), ["reddit", "Reddit"])
_page(S20, "snapchat", "Snapchat 官方 Android（lookup 打开商店页）", C20,
      play("com.snapchat.android"), ["snapchat", "Snapchat"])
_page(S20, "skype", "Skype 官方 Android（lookup 打开商店页）", C20,
      play("com.skype.raider"), ["skype", "Skype"])

# --- 浏览器 ---
C10, S10 = "浏览器", "10-浏览器.json"
_page(S10, "chrome_android", "Google Chrome Android（lookup 打开商店页；开源替代见 fenix/cromite）", C10,
      play("com.android.chrome"), ["chrome", "谷歌浏览器", "Chrome"])
_page(S10, "edge_android", "Microsoft Edge Android（lookup 打开商店页）", C10,
      play("com.microsoft.emmx"), ["edge", "Edge", "微软浏览器"])
_page(S10, "opera_android", "Opera Android（lookup 打开商店页）", C10,
      play("com.opera.browser"), ["opera", "Opera"])
_page(S10, "brave_android", "Brave Android（lookup 打开商店页）", C10,
      play("com.brave.browser"), ["brave", "Brave"])

# --- 音视频 / 短视频 ---
C22, S22 = "音视频", "22-音视频.json"
_page(S22, "youtube", "YouTube 官方 Android（无 GitHub APK；开源客户端搜 newpipe）", C22,
      play("com.google.android.youtube"), ["youtube", "YouTube", "油管"])
_page(S22, "bilibili", "哔哩哔哩 Android（lookup 打开官网）", C22,
      "https://app.bilibili.com/", ["bilibili", "b站", "哔哩哔哩"])
_page(S22, "netflix", "Netflix 官方 Android（lookup 打开商店页）", C22,
      play("com.netflix.mediaclient"), ["netflix", "Netflix"])
_page(S22, "douyin", "抖音 Android（lookup 打开官网）", C22,
      "https://www.douyin.com/downloadpage", ["douyin", "抖音", "tiktok中国"])
_page(S22, "tiktok", "TikTok 官方 Android（lookup 打开商店页）", C22,
      play("com.zhiliaoapp.musically"), ["tiktok", "TikTok"])
_page(S22, "kuaishou", "快手 Android（lookup 打开商店页）", C22,
      play("com.smile.gifmaker"), ["kuaishou", "快手"])
_page(S22, "youku", "优酷 Android（lookup 打开商店页）", C22,
      play("com.youku.phone"), ["youku", "优酷"])
_page(S22, "iqiyi", "爱奇艺 Android（lookup 打开商店页）", C22,
      play("com.qiyi.video"), ["iqiyi", "爱奇艺"])
_page(S22, "capcut_android", "剪映 / CapCut Android（lookup 打开官网）", C22,
      "https://www.capcut.cn/", ["capcut", "jianying", "剪映"])

# --- 音乐 / 社区 ---
C08, S08 = "多媒体", "08-多媒体.json"
_page(S08, "spotify_android", "Spotify 官方 Android（lookup 打开商店页；开源替代 spotube）", C08,
      play("com.spotify.music"), ["spotify", "Spotify"])
_page(S08, "netease_cloud_android", "网易云音乐 Android（lookup 打开官网）", C08,
      "https://music.163.com/#/download", ["netease", "网易云", "网易云音乐"])
_page(S08, "qqmusic_android", "QQ 音乐 Android（lookup 打开官网）", C08,
      "https://y.qq.com/download/download.html", ["qqmusic", "QQ音乐"])

C03, S03 = "写作", "03-写作.json"
_page(S03, "xiaohongshu", "小红书 Android（lookup 打开商店页）", C03,
      play("com.xingin.xhs"), ["xiaohongshu", "小红书", "rednote", "xhs"])
_page(S03, "zhihu", "知乎 Android（lookup 打开商店页）", C03,
      play("com.zhihu.android"), ["zhihu", "知乎"])

# --- 网盘 / 备份 ---
C07, S07 = "备份", "07-备份.json"
_page(S07, "baidunetdisk_android", "百度网盘 Android（lookup 打开官网）", C07,
      "https://pan.baidu.com/download", ["baidunetdisk", "百度网盘", "百度云"])
_page(S07, "aliyundrive_android", "阿里云盘 Android（lookup 打开官网）", C07,
      "https://www.alipan.com/", ["aliyundrive", "阿里云盘", "alipan"])
_page(S07, "googledrive", "Google Drive Android（lookup 打开商店页）", C07,
      play("com.google.android.apps.docs"), ["google drive", "googledrive", "谷歌云盘"])
_page(S07, "onedrive_android", "OneDrive Android（lookup 打开商店页）", C07,
      play("com.microsoft.skydrive"), ["onedrive", "OneDrive"])
_page(S07, "dropbox_android", "Dropbox Android（lookup 打开商店页）", C07,
      play("com.dropbox.android"), ["dropbox", "Dropbox"])

# --- 办公 ---
C04, S04 = "办公", "04-办公.json"
_page(S04, "wps_android", "WPS 办公 Android（lookup 打开官网）", C04,
      "https://www.wps.cn/mobile", ["wps", "WPS", "金山办公"])
_page(S04, "microsoft_365_android", "Microsoft 365 Android（lookup 打开商店页）", C04,
      play("com.microsoft.office.officehubrow"), ["office", "microsoft 365", "Office"])
_page(S04, "google_docs", "Google 文档 Android（lookup 打开商店页）", C04,
      play("com.google.android.apps.docs.editors.docs"), ["google docs", "谷歌文档"])
_page(S04, "notion_android", "Notion Android（lookup 打开商店页）", C04,
      play("notion.id"), ["notion", "Notion"])
_page(S04, "adobe_reader_android", "Adobe Acrobat Reader Android（lookup 打开商店页）", C04,
      play("com.adobe.reader"), ["adobe reader", "acrobat", "PDF"])
_page(S04, "canva_android", "Canva Android（lookup 打开商店页）", C04,
      play("com.canva.editor"), ["canva", "Canva"])

# --- 输入法 ---
C08i, S08i = "输入", "08-输入.json"
_page(S08i, "gboard", "Gboard 谷歌输入法（lookup 打开商店页；开源替代 openboard）", C08i,
      play("com.google.android.inputmethod.latin"), ["gboard", "谷歌输入法", "Gboard"])
_page(S08i, "sogou_pinyin_android", "搜狗输入法 Android（lookup 打开官网）", C08i,
      "https://shouji.sogou.com/", ["sogou", "搜狗", "搜狗输入法"])

# --- 远程 ---
C21, S21 = "远程与协作", "21-远程与协作.json"
_page(S21, "todesk_android", "ToDesk Android（lookup 打开官网）", C21,
      "https://www.todesk.com/download.html", ["todesk", "ToDesk"])
_page(S21, "anydesk_android", "AnyDesk Android（lookup 打开商店页）", C21,
      play("com.anydesk.anydeskandroid"), ["anydesk", "AnyDesk"])
_page(S21, "teamviewer_android", "TeamViewer Android（lookup 打开商店页）", C21,
      play("com.teamviewer.teamviewer.market.mobile"), ["teamviewer", "TeamViewer"])
_page(S21, "sunlogin_android", "向日葵 Android（lookup 打开官网）", C21,
      "https://sunlogin.oray.com/download", ["sunlogin", "向日葵", "oray"])
_page(S21, "zoom_android", "Zoom Android（lookup 打开商店页）", C21,
      play("us.zoom.videomeetings"), ["zoom", "Zoom"])
_page(S21, "teams_android", "Microsoft Teams Android（lookup 打开商店页）", C21,
      play("com.microsoft.teams"), ["teams", "Microsoft Teams"])
_page(S21, "meet_android", "Google Meet Android（lookup 打开商店页）", C21,
      play("com.google.android.apps.meetings"), ["google meet", "meet", "谷歌会议"])

# --- 下载 ---
_page("02-下载.json", "xunlei_android", "迅雷 Android（lookup 打开官网）", "下载",
      "https://www.xunlei.com/", ["xunlei", "thunder", "迅雷"])

# --- 金融 / 支付 ---
_page("27-金融与股票.json", "alipay", "支付宝 Android（lookup 打开官网）", "金融与股票",
      "https://mobile.alipay.com/", ["alipay", "支付宝"])
_page("27-金融与股票.json", "paypal", "PayPal Android（lookup 打开商店页）", "金融与股票",
      play("com.paypal.android.p2pmobile"), ["paypal", "PayPal"])

# --- AI ---
_page("01-AI.json", "chatgpt_android", "ChatGPT 官方 Android（lookup 打开商店页）", "AI",
      play("com.openai.chatgpt"), ["chatgpt", "ChatGPT", "openai"])
_page("01-AI.json", "gemini_android", "Google Gemini Android（lookup 打开商店页）", "AI",
      play("com.google.android.apps.bard"), ["gemini", "Gemini", "bard"])
_page("01-AI.json", "copilot_android", "Microsoft Copilot Android（lookup 打开商店页）", "AI",
      play("com.microsoft.copilot"), ["copilot", "Copilot"])

# --- 游戏 ---
_page("14-游戏.json", "steam_android", "Steam Android（lookup 打开商店页）", "游戏",
      play("com.valvesoftware.android.steam.community"), ["steam", "Steam"])
_page("14-游戏.json", "taptap", "TapTap Android（lookup 打开商店页）", "游戏",
      play("com.taptap"), ["taptap", "TapTap"])

# --- 工具：地图 / 邮箱 / 购物 / 出行 ---
C11, S11 = "工具", "11-工具.json"
_page(S11, "google_maps", "Google 地图 Android（lookup 打开商店页；开源替代 organicmaps/osmand）", C11,
      play("com.google.android.apps.maps"), ["google maps", "谷歌地图", "maps"])
_page(S11, "amap", "高德地图 Android（lookup 打开官网）", C11,
      "https://mobile.amap.com/", ["amap", "高德", "高德地图"])
_page(S11, "baidu_map", "百度地图 Android（lookup 打开商店页）", C11,
      play("com.baidu.BaiduMap"), ["baidu map", "百度地图"])
_page(S11, "gmail", "Gmail Android（lookup 打开商店页）", C11,
      play("com.google.android.gm"), ["gmail", "Gmail"])
_page(S11, "google_keep", "Google Keep Android（lookup 打开商店页）", C11,
      play("com.google.android.keep"), ["keep", "google keep"])
_page(S11, "google_photos", "Google 相册 Android（lookup 打开商店页）", C11,
      play("com.google.android.apps.photos"), ["google photos", "谷歌相册"])
_page(S11, "taobao", "淘宝 Android（lookup 打开商店页）", C11,
      play("com.taobao.taobao"), ["taobao", "淘宝"])
_page(S11, "jd", "京东 Android（lookup 打开商店页）", C11,
      play("com.jingdong.app.mall"), ["jd", "京东", "jingdong"])
_page(S11, "pinduoduo", "拼多多 Android（lookup 打开商店页）", C11,
      play("com.xunmeng.pinduoduo"), ["pinduoduo", "拼多多", "pdd"])
_page(S11, "meituan", "美团 Android（lookup 打开商店页）", C11,
      play("com.sankuai.meituan"), ["meituan", "美团"])
_page(S11, "didi", "滴滴出行 Android（lookup 打开商店页）", C11,
      play("com.sdu.didi.psnger"), ["didi", "滴滴"])
_page(S11, "amazon_android", "Amazon 购物 Android（lookup 打开商店页）", C11,
      play("com.amazon.mShop.android.shopping"), ["amazon", "亚马逊"])

# --- GitHub 可下载 APK ---
_add("13-效率.json", [_apk(
    id="ankidroid",
    简介="AnkiDroid（间隔重复记忆卡片；GitHub universal APK）",
    分类="效率",
    aliases=["anki", "ankidroid", "Anki"],
    installer_markers_match_all=True,
    installer_markers=["AnkiDroid-", "full-universal.apk"],
    href_exclude_substrings=[
        "parallel", "nominify", "amazon", "play", "variant", "dev-", "debug", ".aab",
    ],
    save_name="ankidroid.apk",
    releases_url="https://bgithub.xyz/AnkiDroid/Anki-Android/releases",
    repo_path="AnkiDroid/Anki-Android",
)])
_add("03-写作.json", [_apk(
    id="koreader",
    简介="KOReader（电子书阅读器 Android arm64 APK）",
    分类="写作",
    aliases=["koreader", "KOReader", "电子书"],
    installer_markers_match_all=True,
    installer_markers=["koreader-android-arm64", ".apk"],
    href_exclude_substrings=["kindle", "kobo", "linux", "x86", "android-arm-", "debug"],
    save_name="koreader.apk",
    releases_url="https://bgithub.xyz/koreader/koreader/releases",
    repo_path="koreader/koreader",
)])
_add("16-系统.json", [_apk(
    id="magisk",
    简介="Magisk（Android 开源 Root 方案；GitHub APK，非破解应用商店包）",
    分类="系统",
    aliases=["magisk", "Magisk"],
    installer_markers_match_all=True,
    installer_markers=["Magisk-", ".apk"],
    href_exclude_substrings=["debug", "app-debug", ".aab"],
    save_name="magisk.apk",
    releases_url="https://bgithub.xyz/topjohnwu/Magisk/releases",
    repo_path="topjohnwu/Magisk",
)])
_page("16-系统.json", "kiss_launcher",
      "KISS Launcher（极简启动器；GitHub Release 常无 APK，lookup 打开 Releases）",
      "系统", "https://github.com/Neamar/KISS/releases",
      ["kiss", "KISS", "launcher"])


def main():
    dry = "--dry-run" in sys.argv
    total = 0
    for shard, apps in sorted(BATCH.items()):
        path = os.path.join(MOBILE, "android", shard)
        existing = json.load(open(path, encoding="utf-8")) if os.path.isfile(path) else []
        seen = {(a.get("id") or "").strip() for a in existing if isinstance(a, dict)}
        for app in apps:
            aid = (app.get("id") or "").strip()
            if aid in seen:
                continue
            existing.append(app)
            seen.add(aid)
            total += 1
        if not dry:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)
                f.write("\n")
            print("Wrote", path, "count", len(existing))
    print(f"{'dry-run' if dry else 'done'}: added {total}")


if __name__ == "__main__":
    main()
