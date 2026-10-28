# -*- coding: utf-8 -*-
"""本地清单零命中时，按仓库名在 GitHub 上补一条安装包建议。

选包走 auto_update.link_targets_app（丢掉 blockmap / sig / digest），
下载走 auto_update.download_installer（与 Release 下载同一套镜像再直连）。
默认不写 apps/*.json。
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.parse
from dataclasses import dataclass

import requests

from tools.ui_lang import join_items, t

from auto_update import (
    api_latest_release_url,
    configure_insecure_requests,
    detect_platform_key,
    download_installer,
    github_headers,
    link_targets_app,
    resolve_download_root,
    resolve_tls_verify,
    reveal_in_file_manager,
)

_CACHE_TTL_SEC = 600
_CACHE_MAX = 24
_MEM_CACHE: dict[str, tuple[float, object]] = {}

_MIRRORS = (
    "https://gh-proxy.com/",
    "https://ghp.ci/",
    "https://mirror.ghproxy.com/",
)

_CRACK_RE = re.compile(
    r"(crack(?:ed)?|key[\s-]?gen|re[\s-]?pack|nulled|warez|破解|注册机|破解码|激活补丁)",
    re.I,
)

_JUNK_SUFFIXES = (
    ".blockmap",
    ".sig",
    ".digest",
    ".asc",
    ".minisig",
    ".sha256",
    ".sha512",
    ".sha1",
    ".md5",
    ".sum",
    ".zsync",
    ".yml",
    ".yaml",
    ".json",
    ".txt",
    ".md",
    ".pdb",
    ".xml",
)

_JUNK_PARTS = (
    "checksum",
    "sha256sum",
    "sha512sum",
    "source-code",
    "source_code",
    "source code",
    "dbgsym",
)

_HREF_EXCLUDE = [
    ".blockmap",
    ".sig",
    ".digest",
    ".minisig",
    ".sha256",
    ".sha512",
    ".sha1",
    ".md5",
    "checksum",
    ".zsync",
    "dbgsym",
]

_PROBE = {
    "windows": {
        "installer_markers": [".exe", ".msi"],
        "installer_extensions": [".exe", ".msi"],
        "href_exclude_substrings": _HREF_EXCLUDE,
    },
    "darwin": {
        "installer_markers": [".dmg"],
        "installer_extensions": [".dmg"],
        "href_exclude_substrings": _HREF_EXCLUDE,
    },
    "linux": {
        "installer_markers": [".appimage", ".deb"],
        "installer_extensions": [".appimage", ".deb"],
        "href_exclude_substrings": _HREF_EXCLUDE,
    },
}

# 命中恰好一条才离开 11-工具.json；多条或没有命中都视为拿不准。
_SHARD_RULES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("01-AI.json", "AI", ("large language model", "machine learning", "stable diffusion", "chatgpt", "openai")),
    ("02-下载.json", "下载", ("download manager", "bittorrent", "torrent client")),
    ("07-备份.json", "备份", ("backup tool", "backup software")),
    ("10-安全.json", "安全", ("password manager", "vulnerability scanner")),
    ("12-开发.json", "开发", ("compiler", "programming language", "software development kit")),
    ("14-游戏.json", "游戏", ("game engine", "video game")),
    ("15-笔记.json", "笔记", ("note-taking", "note taking")),
    ("17-终端.json", "终端", ("terminal emulator",)),
    ("22-音视频.json", "音视频", ("media player", "video player", "audio player", "music player")),
    ("23-数据库.json", "数据库", ("postgresql", "mysql", "mongodb", "database server")),
    ("24-云原生.json", "云原生", ("kubernetes", "cloud native")),
    ("25-可观测.json", "可观测", ("observability", "prometheus", "grafana")),
    ("26-编辑器.json", "编辑器", ("text editor", "code editor")),
    ("27-金融与股票.json", "金融与股票", ("stock trading", "stock market")),
    ("28-加密货币.json", "加密货币", ("cryptocurrency", "bitcoin wallet")),
    ("29-局域网文件共享.json", "局域网文件共享", ("file sharing", "lan transfer")),
    ("30-代理与隧道.json", "代理与隧道", ("wireguard", "v2ray", "shadowsocks", "proxy tunnel")),
)

_FALLBACK_SHARD = "11-工具.json"
_FALLBACK_CATEGORY = "工具"
_MIN_LIKENESS = 90


class GitHubSuggestError(Exception):
    def __init__(self, message: str, *, rate_limited: bool = False):
        super().__init__(message)
        self.rate_limited = rate_limited


@dataclass
class RepoHit:
    full_name: str
    name: str
    stars: int
    description: str
    likeness: int
    topics: tuple[str, ...]


@dataclass
class AssetHit:
    name: str
    size: int
    url: str


@dataclass
class Choice:
    repo: RepoHit
    version: str
    asset: AssetHit


def normalize_repo_name(text: str) -> str:
    return re.sub(r"[-_\s]+", "", (text or "")).lower()


def _levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    if abs(len(a) - len(b)) > 3:
        return abs(len(a) - len(b))
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(
                min(
                    cur[j - 1] + 1,
                    prev[j] + 1,
                    prev[j - 1] + (ca != cb),
                )
            )
        prev = cur
    return prev[-1]


def name_likeness(query: str, repo_name: str) -> int:
    """100 = 规范化后完全一致。星标不能把这个分数抬上去。"""
    q = normalize_repo_name(query)
    n = normalize_repo_name(repo_name)
    if not q or not n:
        return 0
    if q == n:
        return 100
    score = 0
    dist = _levenshtein(q, n)
    shorter = min(len(q), len(n))
    if dist == 1 and shorter >= 4:
        score = 96
    elif dist == 2 and shorter >= 8:
        score = 90
    if n.startswith(q) or q.startswith(n):
        ratio = shorter / max(len(q), len(n))
        if ratio >= 0.8:
            score = max(score, 90 + int(round((ratio - 0.8) / 0.2 * 8)))
    return score


def _looks_cracked(*parts: str) -> bool:
    return any(_CRACK_RE.search(p or "") for p in parts)


def _cache_path() -> str:
    base = os.environ.get("TEMP") or os.environ.get("TMP") or os.getcwd()
    return os.path.join(base, "gh-release-fetch-lookup-cache.json")


def _cache_get(key: str):
    now = time.time()
    hit = _MEM_CACHE.get(key)
    if hit and now - hit[0] < _CACHE_TTL_SEC:
        return hit[1]
    path = _cache_path()
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None
    row = data.get(key) if isinstance(data, dict) else None
    if not isinstance(row, dict):
        return None
    ts = row.get("ts") or 0
    if not isinstance(ts, (int, float)) or now - float(ts) >= _CACHE_TTL_SEC:
        return None
    _MEM_CACHE[key] = (float(ts), row.get("data"))
    return row.get("data")


def _cache_set(key: str, value) -> None:
    now = time.time()
    _MEM_CACHE[key] = (now, value)
    path = _cache_path()
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            data = {}
    except (OSError, json.JSONDecodeError):
        data = {}
    data[key] = {"ts": now, "data": value}
    fresh = {
        k: v
        for k, v in data.items()
        if isinstance(v, dict) and now - float(v.get("ts") or 0) < _CACHE_TTL_SEC
    }
    if len(fresh) > _CACHE_MAX:
        ranked = sorted(fresh.items(), key=lambda kv: float(kv[1].get("ts") or 0), reverse=True)
        fresh = dict(ranked[:_CACHE_MAX])
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(fresh, f, ensure_ascii=False)
    except OSError:
        return


def _api_headers() -> dict:
    return {
        **github_headers(),
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _is_rate_limited(response: requests.Response) -> bool:
    if response.status_code not in (403, 429):
        return False
    body = (response.text or "").lower()
    if "rate limit" in body or "secondary rate" in body:
        return True
    return response.headers.get("x-ratelimit-remaining") == "0" and response.status_code == 403


def github_api_get(url: str, verify: bool, stage: str):
    """与下载 GitHub Release 相同的顺序：gh-proxy.com、ghp.ci、mirror.ghproxy.com，最后直连。"""
    headers = _api_headers()
    candidates = [mirror + url for mirror in _MIRRORS] + [url]
    errors: list[str] = []
    saw_rate = False
    for cand in candidates:
        try:
            response = requests.get(cand, headers=headers, timeout=20, verify=verify)
        except requests.RequestException as exc:
            errors.append("%s -> %s" % (cand, exc))
            continue
        if response.status_code == 404:
            if cand == url:
                return None
            errors.append("%s -> HTTP 404" % cand)
            continue
        if _is_rate_limited(response):
            saw_rate = True
            errors.append(t("gh.rate_line", cand, response.status_code))
            continue
        if response.status_code >= 400:
            snippet = (response.text or "").strip().replace("\n", " ")[:160]
            errors.append("%s -> HTTP %s %s" % (cand, response.status_code, snippet))
            continue
        try:
            payload = response.json()
        except ValueError:
            errors.append(t("gh.not_json", cand))
            continue
        if isinstance(payload, dict) and payload.get("message") and "items" not in payload and "tag_name" not in payload and "assets" not in payload:
            message = str(payload.get("message"))
            if "rate limit" in message.lower():
                saw_rate = True
            errors.append("%s -> %s" % (cand, message[:160]))
            continue
        return payload
    if saw_rate:
        raise GitHubSuggestError(
            t("gh.rate", "\n".join(errors[-4:])),
            rate_limited=True,
        )
    detail = "\n".join(errors) if errors else t("gh.no_address")
    raise GitHubSuggestError(t("gh.stage_fail", stage, detail))


def _search_once(query: str, verify: bool, *, quoted: bool) -> list[dict]:
    text = query.strip()
    if quoted:
        # fork:true：GitHub 搜索默认不返回 fork，而有些上游仓库本身是 fork（例如 Open-Shell）。
        q = '"%s" in:name archived:false fork:true' % text.replace('"', "")
    else:
        q = "%s in:name archived:false fork:true" % text
    url = "https://api.github.com/search/repositories?" + urllib.parse.urlencode(
        {"q": q, "per_page": "20"}
    )
    cache_key = "search:" + q
    cached = _cache_get(cache_key)
    if isinstance(cached, list):
        return cached
    payload = github_api_get(url, verify, t("gh.stage_search"))
    items = []
    if isinstance(payload, dict):
        raw = payload.get("items") or []
        if isinstance(raw, list):
            items = [row for row in raw if isinstance(row, dict)]
    _cache_set(cache_key, items)
    return items


def search_repos(query: str, verify: bool) -> list[dict]:
    items = _search_once(query, verify, quoted=True)
    if items:
        return items
    if " " not in query and "-" not in query:
        return items
    return _search_once(query, verify, quoted=False)


def _arch_kind(name: str) -> str:
    n = name.lower()
    if any(k in n for k in ("arm64", "aarch64", "arm-64", "arm_64", "armv7", "armhf", "arm-v7", "armv8")):
        return "other"
    if any(k in n for k in ("x86_64", "x86-64", "amd64", "win64", "x64", "64-bit", "64bit")):
        return "x64"
    if any(k in n for k in ("i686", "i386", "ia32", "win32", "x86_32", "32-bit", "32bit")):
        return "other"
    if re.search(r"(^|[^a-z0-9])x86([^_a-z0-9]|$)", n):
        return "other"
    return "unknown"


def _dmg_kind(name: str) -> str:
    n = name.lower()
    if "universal" in n:
        return "universal"
    if any(k in n for k in ("arm64", "aarch64", "apple-silicon", "applesilicon")):
        return "arm64"
    if any(k in n for k in ("intel", "x86_64", "x86-64", "amd64", "x64")):
        return "intel"
    return "unknown"


def _is_junk_filename(name: str) -> bool:
    n = (name or "").split("?", 1)[0].lower()
    if n.endswith(_JUNK_SUFFIXES):
        return True
    return any(part in n for part in _JUNK_PARTS)


def _asset_passed_link_rules(name: str, url: str, platform: str) -> bool:
    probe = _PROBE.get(platform)
    if not probe:
        return False
    href = (url or name or "").lower()
    if _is_junk_filename(name) or _looks_cracked(name):
        return False
    return link_targets_app(href, (name or "").lower(), probe)


def select_qualified_assets(assets: list[dict], platform: str) -> tuple[list[AssetHit], str]:
    """按平台挑合格安装包。没有合格文件时 reason 说明原因。"""
    rows: list[AssetHit] = []
    for raw in assets:
        if not isinstance(raw, dict):
            continue
        name = (raw.get("name") or "").strip()
        url = (raw.get("browser_download_url") or "").strip()
        if not name or not url:
            continue
        if not _asset_passed_link_rules(name, url, platform):
            continue
        try:
            size = int(raw.get("size") or 0)
        except (TypeError, ValueError):
            size = 0
        rows.append(AssetHit(name=name, size=size, url=url))

    if platform == "windows":
        picked = [a for a in rows if _arch_kind(a.name) != "other"]
        reason = t("gh.reason_win")
    elif platform == "darwin":
        dmgs = rows
        explicit = [a for a in dmgs if _dmg_kind(a.name) in ("arm64", "universal")]
        if explicit:
            picked = explicit
        else:
            picked = [a for a in dmgs if _dmg_kind(a.name) == "unknown"]
        reason = t("gh.reason_mac")
    elif platform == "linux":
        picked = [a for a in rows if _arch_kind(a.name) != "other"]
        reason = t("gh.reason_linux")
    else:
        return [], t("gh.reason_other")

    if picked:
        return picked, ""
    names = [(raw.get("name") or "?") for raw in assets if isinstance(raw, dict)]
    shown = join_items(names[:8]) if names else t("gh.no_files")
    if len(names) > 8:
        shown += t("gh.file_count", len(names))
    return [], t("gh.files_now", reason, shown)


def explain_empty_release(platform: str, tag: str, assets: list) -> str:
    _picked, reason = select_qualified_assets(assets if isinstance(assets, list) else [], platform)
    if tag:
        return t("gh.version", tag, reason)
    return reason


def format_size(size: int) -> str:
    if size <= 0:
        return t("gh.size_unknown")
    if size < 1024:
        return "%d B" % size
    if size < 1024 * 1024:
        return "%.1f KiB" % (size / 1024)
    return "%.1f MiB" % (size / (1024 * 1024))


def _load_root(apps_dir: str) -> dict:
    path = os.path.join(apps_dir, "root.json")
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _rank_repos(query: str, items: list[dict]) -> tuple[list[RepoHit], list[tuple[int, str]]]:
    cracked: list[tuple[int, str]] = []
    ranked: list[RepoHit] = []
    for item in items:
        name = (item.get("name") or "").strip()
        full = (item.get("full_name") or "").strip()
        if not name or not full or item.get("archived"):
            continue
        description = (item.get("description") or "").strip()
        score = name_likeness(query, name)
        if _looks_cracked(name, full, description):
            if score >= _MIN_LIKENESS:
                cracked.append((score, full))
            continue
        if score < _MIN_LIKENESS:
            continue
        topics = item.get("topics") or []
        if not isinstance(topics, list):
            topics = []
        try:
            stars = int(item.get("stargazers_count") or 0)
        except (TypeError, ValueError):
            stars = 0
        ranked.append(
            RepoHit(
                full_name=full,
                name=name,
                stars=stars,
                description=description,
                likeness=score,
                topics=tuple(str(t) for t in topics if t),
            )
        )
    ranked.sort(key=lambda row: (-row.likeness, -row.stars, row.full_name.lower()))
    return ranked, cracked


def _fetch_latest_release(full_name: str, verify: bool) -> tuple[str, list]:
    cache_key = "release:" + full_name.lower()
    cached = _cache_get(cache_key)
    if isinstance(cached, dict) and "tag" in cached and "assets" in cached:
        return str(cached.get("tag") or ""), list(cached.get("assets") or [])

    app = {"id": full_name.split("/")[-1], "repo_path": full_name}
    payload = github_api_get(api_latest_release_url(app), verify, t("gh.stage_release", full_name))
    if payload is None:
        list_url = "https://api.github.com/repos/%s/releases?per_page=5" % full_name
        listed = github_api_get(list_url, verify, t("gh.stage_release_list", full_name))
        payload = None
        if isinstance(listed, list):
            for row in listed:
                if isinstance(row, dict) and not row.get("draft") and (row.get("assets") or []):
                    payload = row
                    break
        if payload is None:
            _cache_set(cache_key, {"tag": "", "assets": []})
            return "", []
    if not isinstance(payload, dict):
        return "", []
    tag = (payload.get("tag_name") or payload.get("name") or "").strip()
    assets = payload.get("assets") if isinstance(payload.get("assets"), list) else []
    slim = []
    for raw in assets:
        if not isinstance(raw, dict):
            continue
        slim.append(
            {
                "name": raw.get("name") or "",
                "size": raw.get("size") or 0,
                "browser_download_url": raw.get("browser_download_url") or "",
            }
        )
    _cache_set(cache_key, {"tag": tag, "assets": slim})
    return tag, slim


def _closest_names(query: str, items: list[dict], limit: int = 3) -> list[str]:
    scored: list[tuple[int, int, str]] = []
    for item in items:
        name = (item.get("name") or "").strip()
        full = (item.get("full_name") or "").strip()
        if not name or not full or item.get("archived"):
            continue
        scored.append((name_likeness(query, name), int(item.get("stargazers_count") or 0), full))
    scored.sort(key=lambda row: (-row[0], -row[1], row[2].lower()))
    out = []
    for score, stars, full in scored[:limit]:
        out.append("%s（相似度 %d，star %d）" % (full, score, stars))
    return out


def _rule_hits(text: str, keywords: tuple[str, ...]) -> bool:
    for kw in keywords:
        if " " in kw or len(kw) >= 12:
            if kw in text:
                return True
            continue
        if re.search(r"(?<![a-z0-9])" + re.escape(kw) + r"(?![a-z0-9])", text):
            return True
    return False


def pick_shard(platform_dir: str, repo: RepoHit) -> tuple[str, str]:
    text = " ".join(
        [repo.name, repo.description, " ".join(repo.topics)]
    ).lower()
    matched = [
        (filename, category)
        for filename, category, keywords in _SHARD_RULES
        if _rule_hits(text, keywords)
    ]
    if len(matched) == 1:
        filename, category = matched[0]
        path = os.path.join(platform_dir, filename)
        if os.path.isfile(path):
            return path, category
    fallback = os.path.join(platform_dir, _FALLBACK_SHARD)
    return fallback, _FALLBACK_CATEGORY


def _catalog_id(repo_name: str) -> str:
    text = repo_name.strip().lower().replace("_", "-").replace(" ", "-")
    text = re.sub(r"[^a-z0-9.\-]+", "", text)
    text = re.sub(r"-{2,}", "-", text).strip("-.")
    return text or "app"


def _existing_ids_and_repos(platform_dir: str) -> tuple[set[str], set[str]]:
    ids: set[str] = set()
    repos: set[str] = set()
    if not os.path.isdir(platform_dir):
        return ids, repos
    for name in os.listdir(platform_dir):
        if not name.endswith(".json"):
            continue
        path = os.path.join(platform_dir, name)
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict) and "apps" in data:
            data = data["apps"]
        if not isinstance(data, list):
            continue
        for app in data:
            if not isinstance(app, dict):
                continue
            app_id = (app.get("id") or "").strip().lower()
            repo = (app.get("repo_path") or "").strip().lower()
            if app_id:
                ids.add(app_id)
            if repo:
                repos.add(repo)
    return ids, repos


def _entry_for(choice: Choice, category: str, platform: str) -> dict:
    brief = (choice.repo.description or choice.repo.full_name).replace("\n", " ").strip()
    if len(brief) > 120:
        brief = brief[:117] + "..."
    entry = {
        "id": _catalog_id(choice.repo.name),
        "简介": brief or choice.repo.name,
        "分类": category,
        "enabled": False,
        "prefer_api_assets": True,
        "version_tag_as_on_github": True,
        "releases_url": "https://bgithub.xyz/%s/releases" % choice.repo.full_name,
        "repo_path": choice.repo.full_name,
        "use_download_filename": True,
        "process_name": "",
        "kill_before_install": False,
        "run_installer": False,
        "href_exclude_substrings": list(_HREF_EXCLUDE),
    }
    if platform == "windows":
        entry["windows_installer"] = True
        entry["installer_extensions"] = [".exe", ".msi"]
    elif platform == "darwin":
        entry["installer_extensions"] = [".dmg"]
    elif platform == "linux":
        entry["installer_extensions"] = [".AppImage", ".deb"]
    return entry


def _append_json_item(path: str, item: dict) -> None:
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            original = f.read()
    else:
        original = "[]\n"
        os.makedirs(os.path.dirname(path), exist_ok=True)
    stripped = original.rstrip()
    if not stripped.endswith("]"):
        raise ValueError("%s 不是 JSON 数组" % path)
    body = stripped[:-1].rstrip()
    newline = "\r\n" if "\r\n" in original else "\n"
    payload = json.dumps(item, ensure_ascii=False, indent=2)
    indented = newline.join(("  " + line) if line else line for line in payload.splitlines())
    if body.endswith("["):
        updated = body + newline + indented + newline + "]" + newline
    else:
        updated = body + "," + newline + indented + newline + "]" + newline
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(updated)
    try:
        with open(path, encoding="utf-8") as f:
            parsed = json.load(f)
        if not isinstance(parsed, list):
            raise ValueError("写回后不是数组")
    except (OSError, json.JSONDecodeError, ValueError):
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(original)
        raise


def save_catalog_entry(apps_dir: str, platform: str, choice: Choice, *, dry_run: bool) -> str | None:
    platform_dir = os.path.join(apps_dir, platform)
    shard_path, category = pick_shard(platform_dir, choice.repo)
    entry = _entry_for(choice, category, platform)
    rel = shard_path
    try:
        rel = os.path.relpath(shard_path, os.path.dirname(apps_dir))
    except ValueError:
        rel = shard_path
    rel = rel.replace("\\", "/")
    ids, repos = _existing_ids_and_repos(platform_dir)
    app_id = entry["id"].lower()
    repo_key = choice.repo.full_name.lower()
    if app_id in ids or repo_key in repos:
        print(t("gh.skip_write", platform, rel))
        return None
    if dry_run:
        print(t("gh.dry_append", rel, entry["id"]))
        return rel
    _append_json_item(shard_path, entry)
    print(t("gh.wrote", rel, entry["id"]))
    return rel


def _print_choice(choice: Choice, platform: str, index: int | None = None) -> None:
    prefix = "[%d] " % index if index else ""
    print(
        t(
            "gh.choice",
            prefix,
            choice.repo.full_name,
            choice.version or "?",
            choice.asset.name,
            format_size(choice.asset.size),
            choice.repo.stars,
        )
    )
    if index is None:
        print(t("gh.platform_line", platform))


def _confirm_enter() -> bool:
    print(t("gh.enter"))
    try:
        if os.name == "nt":
            import msvcrt

            ch = msvcrt.getwch()
            if ch in ("\x00", "\xe0"):
                msvcrt.getwch()
                print()
                print(t("common.cancelled"))
                return False
            print()
            if ch in ("\r", "\n"):
                return True
            print(t("common.cancelled"))
            return False
        if sys.stdin.isatty():
            import termios
            import tty

            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
            print()
            if ch in ("\r", "\n"):
                return True
            print(t("common.cancelled"))
            return False
    except (EOFError, KeyboardInterrupt):
        print("\n" + t("common.cancelled"))
        return False
    print(t("gh.not_tty"))
    return False


def _prompt_index(count: int) -> int | None:
    print(t("gh.pick"))
    try:
        line = input("> ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n" + t("common.cancelled"))
        return None
    if not line:
        print(t("common.cancelled"))
        return None
    if not line.isdigit() or not (1 <= int(line) <= count):
        print(t("gh.bad_index"))
        return None
    return int(line) - 1


def _download_choice(choice: Choice, apps_dir: str, platform: str, verify: bool) -> int:
    cfg = _load_root(apps_dir)
    root = resolve_download_root(cfg)
    if cfg.get("download_subdir_by_platform"):
        root = os.path.join(root, platform)
        os.makedirs(root, exist_ok=True)
    app = {
        "id": _catalog_id(choice.repo.name),
        "repo_path": choice.repo.full_name,
        "prefer_api_assets": True,
        "version_tag_as_on_github": True,
        "use_download_filename": True,
        "releases_url": "https://bgithub.xyz/%s/releases" % choice.repo.full_name,
        "run_installer": False,
    }
    local_filename = os.path.join(root, choice.asset.name)
    try:
        saved = download_installer(
            choice.version or "0",
            choice.asset.url,
            app,
            local_filename,
            verify=verify,
            platform_key=platform,
        )
    except Exception as exc:
        print(t("gh.fail", exc))
        return 1
    print(t("gh.saved", saved))
    reveal_in_file_manager(saved)
    return 0


def _build_choices(query: str, items: list[dict], verify: bool, platform: str) -> tuple[list[Choice], list[str]]:
    ranked, _cracked = _rank_repos(query, items)
    if not ranked:
        return [], []
    best = ranked[0].likeness
    group = [row for row in ranked if row.likeness == best]
    # 星标只决定检查顺序；相似度相同则不靠星标自动拍板。
    group = sorted(group, key=lambda row: (-row.stars, row.full_name.lower()))
    truncated = False
    if len(group) > 5:
        group = group[:5]
        truncated = True
    choices: list[Choice] = []
    notes: list[str] = []
    if truncated:
        notes.append(t("gh.too_many"))
    for repo in group:
        try:
            tag, assets = _fetch_latest_release(repo.full_name, verify)
        except GitHubSuggestError:
            raise
        if not tag and not assets:
            notes.append(t("gh.no_release", repo.full_name))
            continue
        picked, reason = select_qualified_assets(assets, platform)
        if not picked:
            notes.append(t("gh.note", repo.full_name, explain_empty_release(platform, tag, assets)))
            continue
        for asset in picked:
            choices.append(Choice(repo=repo, version=tag, asset=asset))
    choices.sort(
        key=lambda row: (
            -row.repo.likeness,
            -row.repo.stars,
            row.repo.full_name.lower(),
            row.asset.name.lower(),
        )
    )
    return choices, notes


def run_github_suggest(
    *,
    query: str,
    apps_dir: str,
    platform: str | None,
    dry_run: bool,
    no_prompt: bool,
    save: bool,
    insecure: bool,
) -> int:
    plat = (platform or detect_platform_key() or "windows").strip().lower()
    print(t("gh.fallback", plat))
    if plat not in _PROBE:
        print(t("gh.bad_platform", plat))
        return 2

    cfg = _load_root(apps_dir)
    verify = resolve_tls_verify(cfg, insecure)
    configure_insecure_requests(verify)

    try:
        items = search_repos(query, verify)
        if not items:
            print(t("gh.no_repo", query))
            return 2
        ranked, cracked = _rank_repos(query, items)
        exact_cracked = [full for score, full in cracked if score == 100]
        if exact_cracked and not any(row.likeness == 100 for row in ranked):
            print(t("gh.exact_cracked", join_items(exact_cracked[:5])))
            return 2
        if not ranked:
            if cracked:
                print(t("gh.near_cracked", join_items(full for _score, full in cracked[:5])))
                return 2
            nearest = _closest_names(query, items)
            print(t("gh.no_match", query))
            if nearest:
                print(t("gh.nearest", join_items(nearest, semi=True)))
            return 2
        choices, notes = _build_choices(query, items, verify, plat)
    except GitHubSuggestError as exc:
        print(str(exc))
        return 2

    for note in notes:
        print(note)
    if not choices:
        print(t("gh.no_asset"))
        return 2

    unique = len(choices) == 1
    exact = unique and choices[0].repo.likeness == 100
    if unique:
        print(t("gh.suggest"))
        _print_choice(choices[0], plat)
    else:
        repos = {c.repo.full_name for c in choices}
        if len(repos) == 1:
            print(t("gh.one_repo", choices[0].repo.full_name, len(choices)))
        else:
            print(t("gh.multi", len(choices)))
        for i, choice in enumerate(choices, 1):
            _print_choice(choice, plat, index=i)

    if dry_run:
        if not unique:
            print(t("gh.dry_ambiguous"))
            return 2
        print(t("gh.dry_would", choices[0].repo.full_name, choices[0].asset.name))
        if save:
            save_catalog_entry(apps_dir, plat, choices[0], dry_run=True)
        return 0

    if no_prompt:
        if not exact:
            if unique:
                print(t("gh.noprompt_name", choices[0].repo.name))
            else:
                print(t("gh.noprompt_unique"))
            return 2
        if save:
            save_catalog_entry(apps_dir, plat, choices[0], dry_run=False)
        return _download_choice(choices[0], apps_dir, plat, verify)

    if unique:
        if not _confirm_enter():
            return 0
        chosen = choices[0]
    else:
        idx = _prompt_index(len(choices))
        if idx is None:
            return 2
        chosen = choices[idx]

    if save:
        save_catalog_entry(apps_dir, plat, chosen, dry_run=False)
    return _download_choice(chosen, apps_dir, plat, verify)
