"""Merge BoleSync's standalone Switch NRO entries into the published catalog."""
import json
import re
from urllib.parse import quote

import requests

FEED = "https://raw.githubusercontent.com/shellsec/BoleSync/main/catalog/switch-catalog.json"
LIMIT = 2 * 1024 * 1024
PROTECTED_CATEGORIES = {
    "系统基础", "悬浮插件", "引导与维护载荷", "芯片固件", "配套资料与电脑工具",
}
PROTECTED_REPOS = {
    "exploitz86/ascent-toolbox", "team-neptune/deepsea-toolbox",
    "etonedemid/slaunch", "exelix11/switchthemeinjector",
}
CATEGORY_ALIASES = {
    "游戏与模拟器": "游戏与串流", "串流与远程": "云游戏与远程",
    "阅读与学习": "社交与阅读", "日常与通讯": "日常工具",
}
REPO = re.compile(r"[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+")
ASSET = re.compile(r"[\w .()+-]+\.nro", re.IGNORECASE)
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*")


def fetch():
    with requests.get(FEED, timeout=(10, 20), stream=True) as response:
        response.raise_for_status()
        data = bytearray()
        for chunk in response.iter_content(65536):
            data.extend(chunk)
            if len(data) > LIMIT:
                raise ValueError("BoleSync catalog exceeds the size limit")
    return json.loads(data)


def merge(shards, feed):
    """Update the in-memory Switch shards. Return the number of imported entries."""
    if not isinstance(feed, dict) or feed.get("schema") != 1 or not isinstance(feed.get("apps"), list):
        raise ValueError("Unsupported BoleSync catalog schema")

    by_repo = {}
    ids = set()
    categories = {}
    for shard, rows in sorted(shards.items()):
        categories.setdefault(shard.split("-", 1)[1].removesuffix(".json"), shard)
        for row in rows:
            ids.add(row["id"].casefold())
            if row.get("repo_path"):
                by_repo.setdefault(row["repo_path"].casefold(), []).append((shard, row))

    seen = set()
    count = 0
    for source in feed["apps"]:
        if not isinstance(source, dict) or not isinstance(source.get("install"), dict):
            raise ValueError("Invalid BoleSync catalog entry")
        install = source["install"]
        if install.get("mode") != "nro":
            continue
        repo, asset, source_id = source.get("repo"), install.get("asset"), source.get("id")
        if not all(isinstance(value, str) and pattern.fullmatch(value)
                   for value, pattern in ((repo, REPO), (asset, ASSET), (source_id, IDENTIFIER))):
            raise ValueError("Invalid BoleSync NRO repository, attachment or ID")
        if repo.split("/")[1] in {".", ".."} or ".." in asset:
            raise ValueError("Invalid BoleSync repository or attachment path")
        repo_key = repo.casefold()
        category = source.get("category")
        if not isinstance(category, str) or not category.strip():
            raise ValueError("Missing BoleSync category")
        category = CATEGORY_ALIASES.get(category, category)
        if category in PROTECTED_CATEGORIES or repo_key in PROTECTED_REPOS:
            continue
        matches = by_repo.get(repo_key, [])
        if len(matches) > 1 or repo_key in seen:
            raise ValueError(f"Ambiguous Switch catalog repository: {repo}")
        seen.add(repo_key)
        old_shard, row = matches[0] if matches else (None, {})
        if old_shard and (
            row.get("分类") in PROTECTED_CATEGORIES
            or row.get("open_page_only")
            or row.get("installer_extensions") != [".nro"]
        ):
            continue
        if not old_shard:
            if source_id.casefold() in ids:
                raise ValueError(f"BoleSync ID conflicts with a local entry: {source_id}")
            ids.add(source_id.casefold())
            row = {"id": source_id, "save_subdir": source_id, "enabled": False}

        tag = source.get("tag") or row.get("pinned_release_tag") or ""
        if not isinstance(tag, str) or any(part in {"", ".", ".."} for part in tag.split("/") if tag):
            raise ValueError(f"Invalid BoleSync release tag: {repo}")
        name, summary = source.get("name"), source.get("summary")
        if not isinstance(name, str) or not name.strip() or not isinstance(summary, str):
            raise ValueError(f"Invalid BoleSync description: {repo}")
        aliases = source.get("aliases") or []
        if not isinstance(aliases, list) or not all(isinstance(alias, str) for alias in aliases):
            raise ValueError(f"Invalid BoleSync aliases: {repo}")
        previous_aliases = row.get("aliases") or []
        if isinstance(previous_aliases, str):
            previous_aliases = [previous_aliases]
        release = f"https://github.com/{repo}/releases"
        for field in ("download_url_templates", "pinned_release_tag", "release_tag_hint"):
            row.pop(field, None)
        row.update({
            "简介": f"{name}｜{summary}" if summary else name,
            "分类": category,
            "aliases": list(dict.fromkeys([name, *previous_aliases, *aliases])),
            "repo_path": repo,
            "releases_url": f"{release}/tag/{quote(tag, safe='/')}" if tag else f"{release}/latest",
            "prefer_api_assets": True,
            "version_tag_as_on_github": True,
            "installer_extensions": [".nro"],
            "installer_markers": [asset],
            "installer_filename_regex": f"^{re.escape(asset)}$",
            "download_names": [asset],
            "run_installer": False,
            "windows_installer": False,
            "use_download_filename": True,
            "_目录来源": "BoleSync",
        })
        if tag:
            row["pinned_release_tag"] = tag
        instructions = source.get("instructions")
        if isinstance(instructions, str) and instructions:
            previous = row.get("使用说明")
            row["使用说明"] = "\n".join(dict.fromkeys(text for text in (instructions, previous) if text))
        target = categories.get(category, "98-BoleSync.json")
        if target != old_shard:
            if old_shard:
                shards[old_shard].remove(row)
            shards.setdefault(target, []).append(row)
        count += 1
    if not count:
        raise ValueError("BoleSync catalog contains no eligible NRO entries")
    return count
