"""Install a verified, immutable official catalog snapshot."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile
import time
import zipfile

import requests

from tools.app_list import CATALOGS
from tools.download_engine import atomic_json, ranked_routes

RELEASE = "https://github.com/shellsec/gh-release-fetch/releases/download/catalog-data/"
ASSET = "gh-release-fetch-catalog.zip"
PLATFORMS = {(directory, platform) for _, directory, platform, _ in CATALOGS}
DIRECTORIES = {directory for directory, _ in PLATFORMS}
LIMIT = 24 * 1024 * 1024
RETIRED_REPOSITORIES = {"0ad/0ad"}


def is_retired_repository(repo):
    return str(repo or "").strip("/").casefold() in RETIRED_REPOSITORIES


def filter_catalog_page(page):
    pattern = r'(<script id="data" type="application/json">)(.*?)(</script>)'

    def filter_data(match):
        data = json.loads(match[2])
        filtered = {platform: [row for row in rows if not is_retired_repository(row.get("repo"))]
                    for platform, rows in data.items()}
        if filtered == data:
            return match[0]
        payload = json.dumps(filtered, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
        return match[1] + payload + match[3]

    return re.sub(pattern, filter_data, page, count=1, flags=re.DOTALL)


def check_due(root, *, now=None):
    now = time.time() if now is None else now
    try:
        last = float((Path(root) / "catalog-updates/checked-at").read_text(encoding="ascii"))
        return not 0 <= now - last < 7 * 86400
    except (OSError, ValueError):
        return True


def mark_checked(root):
    path = Path(root) / "catalog-updates/checked-at"
    path.parent.mkdir(exist_ok=True)
    atomic_json(path, time.time())


def active_catalog(root, fallback=None):
    root = Path(root)
    snapshot = current_snapshot(root / "catalog-updates", "catalog.html")
    if snapshot != root / "catalog-updates":
        return snapshot
    return Path(fallback) if fallback is not None else root


def current_snapshot(cache, marker):
    try:
        digest = json.loads((cache / "current.json").read_text(encoding="utf-8"))["sha256"]
        if re.fullmatch("[0-9a-f]{64}", digest):
            candidate = cache / digest
            if (candidate / marker).is_file():
                return candidate
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return cache


def allowed(name):
    parts = PurePosixPath(name).parts
    return name == "catalog.html" or (
        len(parts) == 2 and parts[0] in DIRECTORIES and parts[1] == "root.json"
    ) or (
        len(parts) == 3 and parts[:2] in PLATFORMS and re.fullmatch(r"\d{2}-[^/\\:]+\.json", parts[2])
        and name == "/".join(parts)
    )


def independent_categories(config):
    """Read ordered sidebar category names; older catalogs keep Agent Skills."""
    names = config.get("independent_categories", ["Agent Skills"])
    if (not isinstance(names, list) or len(names) > 32
            or any(not isinstance(name, str) or not 1 <= len(name) <= 48
                   or name != name.strip() or ":" in name or not name.isprintable()
                   for name in names)
            or len({name.casefold() for name in names}) != len(names)):
        raise ValueError("独立分类配置格式错误")
    return names


def unpack(source, destination):
    with zipfile.ZipFile(source) as archive:
        seen = set()
        files = archive.infolist()
        if len(files) > 600 or sum(item.file_size for item in files) > LIMIT:
            raise ValueError("目录包超过大小限制")
        for item in files:
            name = item.filename
            if not allowed(name) or name.casefold() in seen:
                raise ValueError(f"目录包包含无效或重复路径：{name}")
            seen.add(name.casefold())
            content = archive.read(item)
            if name.endswith(".json"):
                parsed = json.loads(content.decode("utf-8-sig"))
                expected = dict if name.endswith("/root.json") else list
                if not isinstance(parsed, expected) or isinstance(parsed, list) and any(
                    not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"]
                    for row in parsed
                ):
                    raise ValueError(f"目录数据格式错误：{name}")
                if name == "apps/root.json":
                    independent_categories(parsed)
            elif '<meta name="catalog-session" content="">' not in content.decode("utf-8"):
                raise ValueError("网页目录格式不兼容")
            path = destination / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        if "catalog.html" not in seen or any(
            f"{directory}/root.json" not in seen
            or not any(name.startswith(f"{directory}/{platform}/") for name in seen)
            for directory, platform in PLATFORMS
        ):
            raise ValueError("目录包缺少平台数据或网页目录")


def fetch(url, limit):
    with requests.get(url, stream=True, timeout=(6, 15), headers={"Cache-Control": "no-cache"}) as response:
        response.raise_for_status()
        data = bytearray()
        for chunk in response.iter_content(65536):
            data.extend(chunk)
            if len(data) > limit:
                raise ValueError("服务器响应超过大小限制")
        return bytes(data)


def update(root, report, *, release=RELEASE, fetch_bytes=fetch, routes=ranked_routes):
    return update_bundle(root, report, ASSET, unpack, release=release, fetch_bytes=fetch_bytes, routes=routes)


def update_bundle(root, report, asset, unpack_bundle, *, release=RELEASE, fetch_bytes=fetch,
                  routes=ranked_routes, cache_name="catalog-updates", marker="catalog.html"):
    root = Path(root)
    cache = root / cache_name
    current = current_snapshot(cache, marker).name
    url = release + asset
    attempts = 0
    cached_copy_seen = False

    def read_digest(target):
        sha = fetch_bytes(target + ".sha256", 4096).decode("ascii").strip()
        match = re.fullmatch(r"([0-9a-fA-F]{64})[ \t]+\*?" + re.escape(asset), sha)
        if not match:
            raise ValueError("校验文件格式不正确")
        return match[1].lower()

    def candidates():
        yield "direct", url
        yield from ((name, target) for name, target in routes(url, "auto", lambda _: None)
                    if target != url)

    official_digest = None
    for name, target in candidates():
        attempts += 1
        try:
            if official_digest is None:
                report(f"正在检查目录 · {name}")
                digest = read_digest(target)
                if target == url:
                    official_digest = digest
            else:
                digest = official_digest
            if current == digest:
                if target == url or official_digest is not None:
                    return False
                # An acceleration service can still have an older cached pair.
                cached_copy_seen = True
                continue
            report(f"正在下载目录 · {name}")
            data = fetch_bytes(target, LIMIT)
            if hashlib.sha256(data).hexdigest() != digest:
                raise ValueError("SHA-256 不匹配")
        except (requests.RequestException, ValueError):
            continue
        break
    else:
        if cached_copy_seen:
            raise ValueError("加速线路返回了与本地相同的目录，暂时无法确认最新版本，继续使用现有清单")
        raise ValueError(f"各线路均未返回通过校验的目录包（继续使用现有清单，已尝试 {attempts} 条线路）")
    cache.mkdir(exist_ok=True)
    snapshot = cache / digest
    if not snapshot.exists():
        with tempfile.TemporaryDirectory(prefix=".stage-", dir=cache) as staging:
            stage = Path(staging)
            (stage / "bundle.zip").write_bytes(data)
            (stage / "content").mkdir()
            unpack_bundle(stage / "bundle.zip", stage / "content")
            os.replace(stage / "content", snapshot)
    atomic_json(cache / "current.json", {"sha256": digest})
    return True
