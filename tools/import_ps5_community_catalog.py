#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""导入 PS5 原生应用事实；--refresh 从社区目录刷新并核查作者发布附件。"""
from __future__ import annotations

import argparse
import html
import json
import re
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "apps-ps5" / "community-source.json"
CATALOG = "darkxex/ps5-homebrew-catalog"
CATEGORIES = {
    "emulators": "10-模拟器", "video": "11-影音与直播", "music": "12-音乐",
    "streaming": "13-串流与云游戏", "utilities": "14-工具与个性化",
    "ai": "15-AI", "console-ports": "16-游戏移植", "pc-ports": "16-游戏移植",
    "homebrew-games": "17-自制游戏", "tools": "18-测试工具", "showcases": "18-测试工具",
}
SEARCH_ALIASES = {
    "emulators": ["模拟器"], "video": ["视频", "播放器", "影音"],
    "music": ["音乐", "音频"], "streaming": ["串流", "云游戏", "远程"],
    "utilities": ["工具"], "ai": ["AI", "人工智能"],
    "console-ports": ["游戏移植"], "pc-ports": ["游戏移植"],
    "homebrew-games": ["自制游戏"], "tools": ["测试工具"],
}
PROJECT_ALIASES = {
    "ps5sx2": ["PS2", "PCSX2"], "swanstationps5": ["PS1", "PSX"],
    "psswanstation": ["PS1", "PSX"], "psflycast": ["Dreamcast", "DC"],
    "porpoise": ["Dolphin", "GameCube", "Wii"], "ps5cemu-har": ["Cemu", "Wii U"],
    "ps5_retroarch": ["RetroArch", "全能模拟器"], "prosperostore": ["自制商店", "应用商店"],
    "prospero-explorer": ["文件管理"], "prosperolight": ["Moonlight", "月光"],
    "steam-link-ps5": ["Steam Link", "Steam串流"], "emby5": ["Emby", "Jellyfin"],
    "jelly5": ["Jellyfin"], "spot5": ["Spotify"],
}
FIELDS = ("titleid", "name", "category", "license", "version", "source_repo", "artifact_url", "sha256")


def fetch(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "gh-release-fetch"})
    with urllib.request.urlopen(request, timeout=25) as response:
        return response.read().decode("utf-8")


def verify(path: str, record: dict) -> dict:
    check = {"path": path, "status": "unpublished"}
    url = record.get("artifact_url") or ""
    parsed = urllib.parse.urlparse(url)
    match = re.fullmatch(r"/([^/]+/[^/]+)/releases/download/([^/]+)/([^/]+)", parsed.path)
    if parsed.scheme != "https" or parsed.hostname != "github.com" or not match:
        return check
    repo, tag, filename = match.groups()
    check.update(repo=repo, tag=urllib.parse.unquote(tag), filename=urllib.parse.unquote(filename),
                 release_url=f"https://github.com/{repo}/releases/tag/{tag}")
    try:
        page = fetch(f"https://github.com/{repo}/releases/expanded_assets/{tag}")
        urls = dict.fromkeys(html.unescape(value) for value in re.findall(
            r'href="([^"]+/releases/download/[^"]+)"', page
        ))
        check["assets"] = [{"name": urllib.parse.unquote(value.rsplit("/", 1)[1]),
                            "url": urllib.parse.urljoin("https://github.com", value)} for value in urls]
        check["status"] = "verified" if any(
            urllib.parse.unquote(asset["url"]).lower() == urllib.parse.unquote(url).lower()
            for asset in check["assets"]
        ) else "missing-asset"
    except (OSError, ValueError) as error:
        check.update(status="check-failed", error=str(error))
    return check


def refresh() -> dict:
    tree = json.loads(fetch(f"https://api.github.com/repos/{CATALOG}/git/trees/main?recursive=1"))
    if tree.get("truncated"):
        raise ValueError("社区目录树不完整，未更新本地快照")
    paths = [item["path"] for item in tree["tree"]
             if re.fullmatch(r"apps/[^/]+\.json", item["path"])]
    if not paths:
        raise ValueError("社区目录未返回应用，未更新本地快照")

    def read(path: str) -> dict:
        data = json.loads(fetch(f"https://raw.githubusercontent.com/{CATALOG}/main/{path}"))
        record = {key: data.get(key) for key in FIELDS}
        return {"path": path, "record": record, "check": verify(path, record)}

    with ThreadPoolExecutor(max_workers=6) as pool:
        records = list(pool.map(read, sorted(paths)))
    # A transient failure must not replace previously verified downloads with page-only entries.
    if any(row["check"]["status"] == "check-failed" for row in records):
        raise ValueError("部分作者发布页暂时无法核查，保留本地快照，请稍后重试")
    return {"source": f"https://github.com/{CATALOG}",
            "checked_on": datetime.now(timezone(timedelta(hours=8))).date().isoformat(),
            "说明": "仅核查目录和作者附件存在性；未下载程序、未核对字节摘要、未实机测试。",
            "records": records}


def entries(snapshot: dict) -> tuple[dict, list]:
    groups = {name: [] for name in set(CATEGORIES.values()) | {"19-其他应用"}}
    unpublished = []
    seen = set()
    for row in snapshot["records"]:
        record, check = row["record"], row["check"]
        titleid = record.get("titleid") or ""
        source = record.get("source_repo") or ""
        if not re.fullmatch(r"PPSA\d{5}", titleid) or not source:
            unpublished.append({"name": record.get("name"), "titleid": titleid})
            continue
        parsed = urllib.parse.urlparse(source)
        repo = parsed.path.strip("/")
        if parsed.scheme != "https" or parsed.hostname != "github.com" or not re.fullmatch(r"[^/]+/[^/]+", repo):
            raise ValueError("非法作者仓库地址: " + source)
        aid = "native-" + titleid.lower()
        if aid in seen:
            raise ValueError("重复应用 ID: " + aid)
        seen.add(aid)
        shard = CATEGORIES.get(record.get("category"), "19-其他应用")
        category = shard.split("-", 1)[1]
        note = "原生 PS5 标题；具体固件、启动器与权限要求查看作者 README。"
        if record.get("category") in ("emulators", "console-ports", "pc-ports"):
            note += "所需 BIOS、游戏或商业运行库需按作者说明自行准备。"
        app = {"id": aid, "简介": f"{record['name']}（PS5 {category}）", "分类": category,
               "aliases": [record["name"], titleid, repo.split("/")[-1],
                           *SEARCH_ALIASES.get(record.get("category"), []),
                           *PROJECT_ALIASES.get(repo.split("/")[-1].lower(), [])], "enabled": False,
               "repo_path": repo, "releases_url": source + "/releases", "title_id": titleid,
               "run_installer": False, "kill_before_install": False, "运行方式": "原生标题",
               "固件要求": "按作者 README 与发布说明核对，未统一核定。", "使用说明": note,
               "_目录来源": f"https://github.com/{CATALOG}/blob/main/{row['path']}",
               "_许可": record.get("license"), "_上游sha256": record.get("sha256"),
               "_核查": {"日期": snapshot["checked_on"], "状态": check["status"],
                        "来源": check.get("release_url", source)}}
        filename = check.get("filename", "")
        source_only = bool(re.search(r"source|sourceonly", filename, re.I))
        if check["status"] == "verified" and not source_only and check.get("repo", "").lower() == repo.lower():
            app.update(prefer_api_assets=True, version_tag_as_on_github=True,
                       windows_installer=False, process_name="", pinned_release_tag=check["tag"],
                       releases_url=check["release_url"], installer_extensions=[Path(filename).suffix],
                       installer_markers=[filename], installer_markers_match_all=True,
                       use_download_filename=True, save_name=filename, save_subdir=aid,
                       download_url_templates=[record["artifact_url"]])
            app["_核查"]["发布标签"] = check["tag"]
        else:
            reason = "目录记录的附件当前未核实可用，保留作者页面入口。"
            if source_only:
                reason = "目录链接是源码/构建器包，保留作者页面，不作为主机可运行程序下载。"
            app.update(open_page_only=True, open_page_url=source, _下载说明=reason,
                       使用说明=note + reason)
        groups[shard].append(app)
    return groups, unpublished


def dump(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true", help="联网刷新社区目录和发布附件核查")
    args = parser.parse_args()
    snapshot = refresh() if args.refresh else json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    groups, unpublished = entries(snapshot)
    target = ROOT / "apps-ps5" / "ps5"
    target.mkdir(parents=True, exist_ok=True)
    for shard, apps in sorted(groups.items()):
        path = target / (shard + ".json")
        old = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
        enabled = {app["id"]: app.get("enabled", False) for app in old}
        for app in apps:
            app["enabled"] = enabled.get(app["id"], False)
        dump(path, apps)
    if args.refresh:
        dump(SNAPSHOT, snapshot)
    dump(ROOT / "apps-ps5" / "unpublished.json", unpublished)
    print(f"Imported {sum(map(len, groups.values()))} native app records; {len(unpublished)} unpublished records excluded")


if __name__ == "__main__":
    main()
