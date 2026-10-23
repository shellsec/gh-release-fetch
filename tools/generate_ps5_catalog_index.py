#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""从 apps-ps5 分类分片生成 PS5 使用索引，不联网。"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def main() -> None:
    apps = [app for path in sorted((ROOT / "apps-ps5" / "ps5").glob("*.json"))
            for app in json.loads(path.read_text(encoding="utf-8"))]
    if len({app["id"] for app in apps}) != len(apps):
        raise ValueError("PS5 清单有重复 ID")
    downloadable = sum(not app.get("open_page_only") for app in apps)
    unpublished = json.loads((ROOT / "apps-ps5" / "unpublished.json").read_text(encoding="utf-8"))
    lines = [
        "# PS5 独立清单", "",
        "> 自动生成：`python tools/generate_ps5_catalog_index.py`。", "",
        f"共 **{len(apps)} 项**：**{downloadable} 项有已核查下载附件**，"
        f"**{len(apps) - downloadable} 项为页面入口**。仅登记名称的 {len(unpublished)} 个项目未计入应用清单。", "",
        "## 搜索与下载", "",
        "运行 `python lookup_app.py`，选择 **5：PS5**，再输入关键词、选择结果和操作；"
        "也可直接运行 `lookup_ps5.bat`。", "",
        "```bat", "lookup_ps5.bat 模拟器", "lookup_ps5.bat PS2", "lookup_ps5.bat 播放器",
        "lookup_ps5.bat FTP", "python auto_update.py --apps-dir apps-ps5 --platform ps5 ftpsrv",
        "python tools/run_saved_apps.py ps5 --apps-dir apps-ps5", "```", "",
        "下载保留原文件名，保存到 `ps5/<id>/`。默认条目关闭；可以显式指定 ID 下载，"
        "或在搜索结果中加入 `saved_apps_ps5.json` 更新列表。仅下载，不安装、不解压、不发送载荷。", "",
        "Windows 可直接打开根目录 lookup_app.exe 选择 PS5；搜索、下载和保存列表 EXE 已同步重打包。"
        "BAT 在 Python 依赖齐全且源码存在时使用源码，否则使用 EXE。"
        "本地未命中时通用 GitHub 补搜尚不支持 PS5 附件筛选。", "",
        "## 运行方式与版本", "",
        "浏览器入口、HEN 环境、ELF 服务、websrv 应用、原生标题和电脑端 SDK 是不同内容。"
        "各条目的固件范围、权限、启动器、额外资源需分别查看作者说明；入口支持某版本，"
        "不表示本清单全部软件都支持该版本。本次未在 PS5 实机运行。", "",
        "基础工具通常跟随作者最新稳定 Release；原生应用和需要配套的 websrv 包固定到核查标签，"
        "避免目录记录与实际附件不一致。带 beta/alpha/preview 的版本保持作者标记，不改称稳定版。", "",
        "社区应用由 [PS5 Homebrew Catalog](https://github.com/darkxex/ps5-homebrew-catalog) 发现，"
        "下载仍来自各作者的 GitHub Release。已逐项核对附件名；源码包、已缺失附件保留页面入口。"
        "目录提供的 SHA256 仅作上游记录，本工具当前没有以实际下载字节验证这些摘要。", "",
        "原生 RetroArch、websrv 的 RetroArch 前端/核心、websrv 内置 RetroArch 包属于不同分发，"
        "不要将其解压布局混用。模拟器的 BIOS、游戏数据、部分运行库由用户按作者说明准备。", "",
        "## 分类概览", "", "| 分类 | 项目数 |", "|---|---|",
    ]
    lines.extend(f"| {cell(category)} | {count} |" for category, count in Counter(
        app["分类"] for app in apps
    ).items())
    titles = defaultdict(list)
    for app in apps:
        if app.get("title_id"):
            titles[app["title_id"]].append(app["id"])
    collisions = {key: values for key, values in titles.items() if len(values) > 1}
    if collisions:
        lines += ["", "## 相同 Title ID 的不同项目", "",
                  "以下条目报告了相同 Title ID，不能据此认为可以同时安装；请核对作者说明。", "",
                  "| Title ID | 条目 |", "|---|---|"]
        lines.extend(f"| {title} | {', '.join(ids)} |" for title, ids in sorted(collisions.items()))
    for category in dict.fromkeys(app["分类"] for app in apps):
        lines += ["", "## " + category, "", "| ID / 项目 | 运行方式 / 下载 | 说明 |", "|---|---|---|"]
        for app in (item for item in apps if item["分类"] == category):
            url = app.get("open_page_url") or app.get("releases_url")
            label = f"`{app['id']}` — [{cell(app['简介'])}]({url})"
            content = app.get("运行方式", "") + "；"
            content += "页面入口" if app.get("open_page_only") else "/".join(app["installer_extensions"])
            if app.get("pinned_release_tag"):
                content += "；固定 " + app["pinned_release_tag"]
            note = app.get("使用说明", "") + " 固件：" + app.get("固件要求", "查看作者说明。")
            lines.append(f"| {label} | {cell(content)} | {cell(note)} |")
    lines += ["", "## 维护与核查", "",
              "核心工具的核查记录见 [release-check.json](apps-ps5/release-check.json)，"
              "社区应用作者链接和附件核查见 [community-source.json](apps-ps5/community-source.json)。", "",
              "```bat", "python tools/import_ps5_community_catalog.py --refresh",
              "python tools/generate_ps5_catalog_index.py", "```", "",
              "不带 --refresh 时只从本地快照重建社区分片。导入器保留同一 ID 的 enabled 状态，"
              "生成的 10–19 号分片由脚本维护；自定义条目放在其他分片以免被刷新覆盖。"
              "核查暂时失败时不覆盖已有快照。", "",
              "待关注但未发布的名称见 [unpublished.json](apps-ps5/unpublished.json)，"
              "不会把这些登记项当成已经存在的下载包。", ""]
    (ROOT / "CATALOG.ps5.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"PS5: {len(apps)} entries, {downloadable} downloadable, {len(apps) - downloadable} page-only")


if __name__ == "__main__":
    main()
