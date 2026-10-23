#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""从 Switch JSON 分片生成使用索引；只读清单，不联网、不修改 enabled。"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def main() -> None:
    apps = []
    seen = set()
    for path in sorted((ROOT / "apps-switch" / "switch").glob("*.json")):
        for app in json.loads(path.read_text(encoding="utf-8")):
            if app["id"] in seen:
                raise ValueError("Switch 重复 ID: " + app["id"])
            seen.add(app["id"])
            apps.append(app)

    downloadable = sum(not app.get("open_page_only") for app in apps)
    pinned = sum(bool(app.get("pinned_release_tag")) for app in apps)
    lines = [
        "# Switch 独立清单",
        "",
        "> 自动生成：`python tools/generate_switch_catalog_index.py`；修改 JSON 分片后重新生成。",
        "",
        "与电脑端 `apps/`、移动端 `apps-mobile/` 分开维护。"
        "仅下载，不安装、不解压、不刷写。",
        "",
        f"共 **{len(apps)} 条**：**{downloadable} 条可下载**、"
        f"**{len(apps) - downloadable} 条页面入口**。其中 {pinned} 条为固定 tag 的预发布版本。",
        "",
        "逐项对照你提供的整合包组件，见 [组件对照表](apps-switch/COMPONENTS.md)。",
        "",
        "## 使用入口",
        "",
        "运行 `python lookup_app.py`，选择 **4：Switch**；也可直接搜索：",
        "",
        "```bat",
        "lookup_switch.bat 大气层",
        "lookup_switch.bat 存档",
        "lookup_switch.bat 投屏",
        "python auto_update.py --apps-dir apps-switch --platform switch atmosphere-stable nx-firmware",
        "python tools/run_saved_apps.py switch --apps-dir apps-switch",
        "```",
        "",
        "搜索后可下载、加入更新列表或打开项目页。条目默认关闭；"
        "显式指定 ID 可直接下载，启用后可批量更新。保存列表为 `saved_apps_switch.json`。",
        "",
        "附件保留原文件名，保存到 `switch/<id>/`。NRO、OVL、NSP、BIN 载荷与固件压缩包都只下载，"
        "安装和复制到 SD 卡需按项目说明进行。",
        "",
        "Windows 可直接打开根目录 lookup_app.exe，选择 4：Switch；相关 EXE 已同步重打包。"
        "BAT 在 Python 依赖齐全且源码存在时使用源码，否则使用 EXE。"
        "Switch 搜索目前以本地清单为准，未命中时通用 GitHub 补搜不支持 Switch 附件筛选。",
        "",
        "## 分类概览",
        "",
        "| 分类 | 条目数 |",
        "|---|---|",
    ]
    lines.extend(f"| {cell(category)} | {count} |" for category, count in Counter(
        app["分类"] for app in apps
    ).items())
    lines += [
        "",
        "## 清单与下载规则",
        "",
        "“可下载”表示已匹配公开发布附件，不表示已经过实机测试。"
        "核查日期、标签与文件名快照见 [release-check.json](apps-switch/release-check.json)。"
        "发布时间较早也不直接等于停更，兼容性需查看各项目说明。",
    ]
    for category in dict.fromkeys(app["分类"] for app in apps):
        lines += ["", "### " + category, "", "| ID / 项目 | 下载内容 | 使用说明 |", "|---|---|---|"]
        for app in (item for item in apps if item["分类"] == category):
            url = app.get("open_page_url") or app.get("releases_url", "")
            label = f"`{app['id']}` — [{cell(app['简介'])}]({url})"
            if app.get("open_page_only"):
                content = "页面入口"
            else:
                content = " / ".join(app["installer_extensions"])
                if app.get("pinned_release_tag"):
                    content += "；预发布固定 `" + app["pinned_release_tag"] + "`"
            note = app.get("使用说明") or app.get("_下载说明") or "查看项目说明。"
            lines.append(f"| {label} | {cell(content)} | {cell(note)} |")
    lines += [
        "",
        "## 后续维护",
        "",
        "在 `apps-switch/switch/` 中维护分类 JSON 数组，ID 在 Switch 平台内必须唯一。"
        "名称和中文搜索词填入 `aliases`；资源或插件依赖写入 `使用说明`。",
        "",
        "下载规则应匹配 Switch 的发布附件，排除电脑端、3DS、Wii U、源码、校验文件和调试包。"
        "有完整 SD 布局包时优先完整包，避免遗漏资源；禁止只凭扩展名选多平台附件。",
        "",
        "预发布项目通过 `pinned_release_tag` 固定到已核查版本，后续需人工复核并更新标签。"
        "普通条目仍动态解析最新稳定 Release。",
        "",
        "页面入口说明具体原因：无公开 Release、Release 无附件、官方外部分发或商店分发。"
        "确认新包后再补规则，不把源码包当作主机程序。",
        "",
        "更新分片与核查快照后运行 `python tools/generate_switch_catalog_index.py` 刷新本页。",
        "",
    ]
    (ROOT / "CATALOG.switch.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Switch: {len(apps)} entries, {downloadable} downloadable, {pinned} pinned prereleases")


if __name__ == "__main__":
    main()
