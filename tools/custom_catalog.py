"""Custom application catalog: inspect sources, preview imports and manage entries."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import time
from urllib.parse import unquote, urlparse

from tools.app_list import CATALOGS, PLATFORMS
from tools.ui_lang import display_term, t

CUSTOM_DIR = "apps-custom"
SHARD = "11-自定义.json"
LABELS = {platform: label for label, _, platform, _ in CATALOGS}


def _platform_label(platform: str) -> str:
    if platform == "linux_handheld":
        return t("catalog.handheld")
    return LABELS.get(platform, platform)


def _enter_default(default: str) -> str:
    return t("cc.enter_default", default) if default else ""
_EXTENSIONS = (".tar.gz", ".tar.xz", ".tar.bz2", ".tar.zst", ".appimage", ".msixbundle", ".appxbundle", ".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm", ".apk", ".ipa", ".vpk", ".nro", ".nsp", ".ovl", ".elf", ".bin", ".zip", ".7z", ".rar", ".tar", ".msix", ".appx")
_VERSION = r"v?[0-9]+(?:[._-][0-9]+)+(?:[-+._]?(?:alpha|beta|rc|pre|dev|preview)[._-]?[0-9]*)?"


def parse_source(text: str) -> dict:
    text = text.strip().replace("\\:", ":").rstrip("\\")
    for prefix in ("https://gh-proxy.com/", "https://ghp.ci/", "https://mirror.ghproxy.com/"):
        if text.startswith(prefix):
            text = text[len(prefix):]
            if text.startswith("github.com/"):
                text = "https://" + text
            break
    if re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", text):
        text = "https://github.com/" + text
    parsed = urlparse(text)
    if not parsed.scheme:
        if not text or "://" in text:
            raise ValueError(t("err.need_source"))
        return {"kind": "search", "query": text}
    if parsed.scheme not in ("https", "http") or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError(t("err.http_only"))
    if parsed.hostname.lower() != "github.com":
        return {"kind": "fixed", "url": text, "asset": unquote(parsed.path.rsplit("/", 1)[-1])}
    parts = [unquote(p) for p in parsed.path.strip("/").split("/")]
    if len(parts) < 2 or not all(re.fullmatch(r"[A-Za-z0-9_.-]+", p) for p in parts[:2]):
        raise ValueError(t("err.need_owner"))
    repo = "/".join(parts[:2]).removesuffix(".git")
    rest = parts[2:]
    tag = asset = ""
    if rest in ([], ["releases"], ["releases", "latest"]):
        pass
    elif len(rest) >= 3 and rest[:2] == ["releases", "tag"]:
        tag = "/".join(rest[2:])
    elif len(rest) >= 4 and rest[:2] == ["releases", "download"]:
        tag, asset = "/".join(rest[2:-1]), rest[-1]
    elif len(rest) == 4 and rest[:3] == ["releases", "latest", "download"]:
        asset = rest[-1]
    else:
        raise ValueError(t("err.need_release_url"))
    return {"kind": "github", "repo": repo, "tag": tag, "asset": asset, "url": text}


def _extension(name: str) -> str:
    return next((ext for ext in _EXTENSIONS if name.lower().endswith(ext)), "")


def _platforms(name: str, repo: str, ext: str) -> tuple[str, ...]:
    text = (name + " " + repo).lower()
    tokens = set(re.split(r"[^a-z0-9]+", text))
    if ext in (".nro", ".nsp", ".ovl"):
        return ("switch",)
    if ext == ".vpk":
        return ("vita",)
    if ext == ".ipa":
        return ("ios",)
    if ext == ".apk":
        return ("android_tv",) if tokens & {"tv", "androidtv", "leanback"} else ("android", "android_tv")
    if ext in (".exe", ".msi"):
        return ("windows",)
    if tokens & {"ps4", "ps5", "vita", "psvita", "switch", "xbox"}:
        return tuple(p for p in ("ps4", "ps5", "vita", "switch", "xbox") if p in tokens or (p == "vita" and "psvita" in tokens))
    if ext in (".msix", ".appx", ".msixbundle", ".appxbundle"):
        return ("windows",)
    if ext == ".dmg":
        return ("darwin",)
    if ext in (".appimage", ".deb", ".rpm"):
        return ("linux", "linux_handheld")
    if tokens & {"steamdeck", "steamos", "handheld"}:
        return ("linux_handheld",)
    if tokens & {"windows", "win", "win32", "win64"}:
        return ("windows",)
    if tokens & {"darwin", "mac", "macos", "osx"}:
        return ("darwin",)
    if "linux" in tokens:
        return ("linux", "linux_handheld")
    return ()


def detect_assets(assets: list[dict], repo: str = "") -> list[dict]:
    out = []
    for raw in assets:
        name = str(raw.get("name") or "")
        ext = _extension(name)
        low = name.lower()
        if not ext or re.search(r"(?:^|[._ -])(sources?|checksums?|debug|dbgsym)(?:[._ -]|$)", low):
            continue
        if re.search(r"(?:arm64|aarch64|arm64-v8a)", low):
            arch = "ARM64"
        elif re.search(r"(?:armeabi|armv7|armhf)", low):
            arch = "ARM32"
        elif re.search(r"(?:x86_64|amd64|x64)", low):
            arch = "x64"
        elif re.search(r"(?:ia32|i[3-6]86|x86)(?!_64)", low):
            arch = "x86"
        elif "universal" in low:
            arch = "通用"
        else:
            arch = "未标明"
        kind = "绿色/便携版" if re.search(r"green|portable", low) else ("安装版" if ext in (".exe", ".msi", ".dmg", ".apk", ".vpk", ".msixbundle") else "发布附件")
        out.append({"name": name, "url": raw.get("browser_download_url") or raw.get("url") or "", "extension": ext, "platforms": _platforms(name, repo, ext), "architecture": arch, "package_kind": kind})
    return out


def filename_pattern(name: str, tag: str) -> str:
    # Only the version segment varies. Architecture, OS and package variant remain literal.
    version = tag.lstrip("v")
    if version and len(version) >= 3 and version in name:
        start = name.index(version)
        return re.escape(name[:start]) + r"[0-9][0-9A-Za-z.+_-]*?" + re.escape(name[start + len(version):])
    match = re.search(_VERSION, name, re.I)
    if match:
        return re.escape(name[:match.start()]) + _VERSION + re.escape(name[match.end():])
    return re.escape(name)


def _identifier(value: str, profile: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")[:64] or "custom_app"
    return slug + "_" + hashlib.sha256(profile.encode()).hexdigest()[:10]


def _base(name: str, category: str) -> dict:
    if not isinstance(name, str) or not name.strip():
        raise ValueError(t("err.name_empty"))
    if not isinstance(category, str):
        raise ValueError(t("err.category_text"))
    return {"简介": name.strip(), "分类": category.strip() or "自定义", "enabled": False, "run_installer": False, "windows_installer": False, "use_download_filename": True}


def make_github_entry(repo: str, tag: str, asset: dict, platform: str, name: str, category: str) -> dict:
    pattern = filename_pattern(asset["name"], tag)
    entry = _base(name, category)
    entry.update(id=_identifier(repo, platform + ":" + pattern.lower()), repo_path=repo, releases_url="https://github.com/" + repo + "/releases", prefer_api_assets=True, version_tag_as_on_github=True, installer_markers=[asset["extension"]], installer_extensions=[asset["extension"]], installer_filename_regex=pattern, custom_source="https://github.com/" + repo, custom_asset_name=asset["name"], custom_release_tag=tag, custom_update_mode="github", custom_architecture=asset["architecture"], custom_package_kind=asset["package_kind"])
    entry["save_subdir"] = entry["id"]
    return entry


def make_fixed_entry(url: str, platform: str, name: str, category: str, filename: str = "") -> dict:
    source = parse_source(url)
    if source["kind"] != "fixed":
        raise ValueError(t("err.github_asset"))
    filename = filename or source["asset"]
    if not filename or filename in (".", "..") or any(ch in filename for ch in '/\\:*?"<>|'):
        raise ValueError(t("err.bad_filename"))
    entry = _base(name, category)
    entry.update(id=_identifier(filename, platform + ":" + url), fixed_download_url=url, custom_source=url, custom_asset_name=filename, custom_update_mode="fixed", save_name=filename, use_download_filename=False)
    entry["save_subdir"] = entry["id"]
    return entry


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def list_entries(custom_dir: str) -> list[dict]:
    root = Path(custom_dir)
    rows = []
    for platform in PLATFORMS:
        files = sorted((root / platform).glob("*.json"))
        if (root / (platform + ".json")).is_file():
            files.append(root / (platform + ".json"))
        for path in files:
            try:
                apps = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError) as e:
                raise ValueError(t("err.read_catalog", path, e)) from e
            if not isinstance(apps, list) or any(not isinstance(a, dict) or not a.get("id") for a in apps):
                raise ValueError(t("err.bad_shard", path))
            for app in apps:
                rows.append({"platform": platform, "app": app, "path": path, "id": app["id"], "apps_dir": str(root), "downloadable": not app.get("open_page_only", False)})
    return rows


def _backup_catalog(custom_dir: str) -> None:
    root = Path(custom_dir)
    files = {str(row["path"].relative_to(root)).replace("\\", "/"): row["path"].read_text(encoding="utf-8") for row in list_entries(custom_dir)}
    # Include empty shards so a delete/add can also be reversed exactly.
    for platform in PLATFORMS:
        for path in (root / platform).glob("*.json"):
            files[path.relative_to(root).as_posix()] = path.read_text(encoding="utf-8")
    _write_json(root / ".backups" / (str(time.time_ns()) + ".json"), {"files": files})
    for old in sorted((root / ".backups").glob("*.json"))[:-20]:
        old.unlink()


def undo_last_change(custom_dir: str) -> bool:
    root = Path(custom_dir)
    backups = sorted((root / ".backups").glob("*.json"))
    if not backups:
        return False
    snapshot = json.loads(backups[-1].read_text(encoding="utf-8"))
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("files"), dict):
        raise ValueError(t("err.bad_backup"))
    restored = {}
    for relative, content in snapshot["files"].items():
        parts = Path(relative).parts
        valid = (len(parts) == 2 and parts[0] in PLATFORMS and parts[1].endswith(".json")) or (len(parts) == 1 and relative.removesuffix(".json") in PLATFORMS)
        path = root / relative
        if not valid or not path.resolve().is_relative_to(root.resolve()):
            raise ValueError(t("err.bad_backup_path"))
        apps = json.loads(content)
        if not isinstance(apps, list):
            raise ValueError(t("err.bad_backup"))
        restored[path] = apps
    current = {row["path"] for row in list_entries(custom_dir)}
    for platform in PLATFORMS:
        current.update((root / platform).glob("*.json"))
    for path, apps in restored.items():
        _write_json(path, apps)
    for path in current - restored.keys():
        path.unlink()
    backups[-1].unlink()
    return True


def export_entries(custom_dir: str) -> dict:
    return {"format": "gh-release-fetch-custom-v1", "entries": [{"platform": row["platform"], "app": row["app"]} for row in list_entries(custom_dir)]}


def _validated_import(bundle: dict) -> list[tuple[str, dict]]:
    if not isinstance(bundle, dict) or bundle.get("format") != "gh-release-fetch-custom-v1" or not isinstance(bundle.get("entries"), list):
        raise ValueError(t("err.bad_export"))
    entries = []
    for row in bundle["entries"]:
        if not isinstance(row, dict):
            raise ValueError(t("err.bad_import_entry"))
        platform, original = row.get("platform"), row.get("app")
        if platform not in PLATFORMS or not isinstance(original, dict) or not isinstance(original.get("id"), str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", original["id"]):
            raise ValueError(t("err.bad_import_platform"))
        if original.get("fixed_download_url"):
            app = make_fixed_entry(original["fixed_download_url"], platform, original.get("简介", ""), original.get("分类", "自定义"), original.get("custom_asset_name", ""))
        else:
            repo = original.get("repo_path") or ""
            source = parse_source(repo)
            assets = detect_assets([{"name": original.get("custom_asset_name", "")}], repo)
            if source.get("kind") != "github" or not assets:
                raise ValueError(t("err.import_missing"))
            app = make_github_entry(source["repo"], original.get("custom_release_tag", ""), assets[0], platform, original.get("简介", ""), original.get("分类", "自定义"))
        app["id"] = original["id"]
        app["save_subdir"] = app["id"]
        entries.append((platform, app))
    return entries


def import_entries(custom_dir: str, bundle: dict, *, replace: bool = False) -> None:
    save_entries(custom_dir, _validated_import(bundle), replace=replace)


def load_preferences(custom_dir: str) -> dict:
    try:
        prefs = json.loads((Path(custom_dir) / ".preferences.json").read_text(encoding="utf-8"))
        return prefs if isinstance(prefs, dict) else {}
    except (OSError, ValueError):
        return {}


def save_preferences(custom_dir: str, preferences: dict) -> None:
    allowed = {key: str(preferences[key]) for key in ("platform", "architecture", "package_kind") if preferences.get(key)}
    _write_json(Path(custom_dir) / ".preferences.json", allowed)


def preferred_asset_indices(assets: list[dict], prefs: dict) -> list[int]:
    scores = [3 * int(bool(prefs.get("architecture")) and a["architecture"] == prefs["architecture"]) + 2 * int(bool(prefs.get("platform")) and prefs["platform"] in a["platforms"]) + int(bool(prefs.get("package_kind")) and a["package_kind"] == prefs["package_kind"]) for a in assets]
    best = max(scores, default=0)
    return [i for i, score in enumerate(scores) if score == best] if best else []


def save_entries(custom_dir: str, entries: list[tuple[str, dict]], *, replace: bool = False, remove_target: tuple[str, str] | None = None) -> None:
    root = Path(custom_dir)
    existing = list_entries(custom_dir)
    by_key = {(row["platform"], row["id"]): row for row in existing}
    edits: dict[Path, list] = {}
    incoming = set()
    for platform, app in entries:
        if platform not in PLATFORMS or not app.get("id"):
            raise ValueError(t("err.bad_id"))
        key = (platform, app["id"])
        if key in incoming:
            raise ValueError(t("err.duplicate_add"))
        incoming.add(key)
        old = by_key.get(key)
        if old and not replace:
            raise ValueError(t("err.exists", *key))
        path = old["path"] if old else root / platform / SHARD
        if path not in edits:
            edits[path] = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
        new_app = dict(app)
        if old:
            new_app["enabled"] = old["app"].get("enabled", False)
            edits[path] = [new_app if a["id"] == app["id"] else a for a in edits[path]]
        else:
            edits[path].append(new_app)
    if remove_target and remove_target not in incoming:
        previous = by_key.get(remove_target)
        if previous:
            path = previous["path"]
            apps = edits.get(path)
            if apps is None:
                apps = json.loads(path.read_text(encoding="utf-8"))
            edits[path] = [a for a in apps if a["id"] != remove_target[1]]
    if not entries:
        return
    _backup_catalog(custom_dir)
    for path, apps in edits.items():
        _write_json(path, apps)
    if not (root / "root.json").exists():
        _write_json(root / "root.json", {"platform_keys": list(PLATFORMS), "download_dir": ".", "download_subdir_by_platform": True, "ssl_verify": True})


def edit_entry(custom_dir: str, platform: str, app_id: str, changes: dict) -> None:
    row = next((r for r in list_entries(custom_dir) if (r["platform"], r["id"]) == (platform, app_id)), None)
    if not row:
        raise ValueError(t("err.missing_entry"))
    allowed = {k: v for k, v in changes.items() if k in ("简介", "分类", "enabled")}
    if "简介" in allowed and not str(allowed["简介"]).strip():
        raise ValueError(t("err.name_empty"))
    apps = json.loads(row["path"].read_text(encoding="utf-8"))
    _backup_catalog(custom_dir)
    _write_json(row["path"], [{**app, **allowed} if app["id"] == app_id else app for app in apps])


def delete_entry(custom_dir: str, platform: str, app_id: str) -> None:
    row = next((r for r in list_entries(custom_dir) if (r["platform"], r["id"]) == (platform, app_id)), None)
    if not row:
        raise ValueError(t("err.missing_entry"))
    apps = json.loads(row["path"].read_text(encoding="utf-8"))
    _backup_catalog(custom_dir)
    _write_json(row["path"], [app for app in apps if app["id"] != app_id])


def _select_indices(text: str, count: int) -> list[int]:
    if text.strip().lower() in ("a", "all", "全部"):
        return list(range(count))
    if not text.strip() or text.strip() == "0":
        return []
    try:
        indices = sorted({int(s.strip()) - 1 for s in text.replace("，", ",").split(",")})
    except ValueError as e:
        raise ValueError(t("err.bad_index")) from e
    if any(i < 0 or i >= count for i in indices):
        raise ValueError(t("err.index_range"))
    return indices


def _pick_platforms(asset: dict, prefs: dict | None = None) -> list[str]:
    guesses = asset["platforms"]
    if len(guesses) == 1:
        return list(guesses)
    choices = guesses or PLATFORMS
    print(t("cc.pick_platform", asset["name"]))
    for i, platform in enumerate(choices, 1):
        print("  %d  %s" % (i, _platform_label(platform)))
    default = str(choices.index(prefs["platform"]) + 1) if prefs and prefs.get("platform") in choices else ""
    text = input(t("cc.platform_prompt", _enter_default(default)))
    return [choices[i] for i in _select_indices(text.strip() or default, len(choices))]


def inspect_github(source: dict, *, verify: bool = True) -> tuple[dict, str, list[dict]]:
    from tools.lookup_github_suggest import github_api_get, search_repos
    if source["kind"] == "search":
        repos = search_repos(source["query"], verify)
        if not repos:
            raise ValueError(t("err.no_github"))
        repos = repos[:10]
        for i, repo in enumerate(repos, 1):
            print("  %d  %s · %s" % (i, repo["full_name"], (repo.get("description") or "")[:100]))
        indexes = _select_indices(input(t("cc.pick_repo")), len(repos))
        if not indexes:
            return {}, "", []
        if len(indexes) != 1:
            raise ValueError(t("err.one_repo"))
        source = {"kind": "github", "repo": repos[indexes[0]]["full_name"], "tag": "", "asset": ""}
    repo = github_api_get("https://api.github.com/repos/" + source["repo"], verify, t("gh.stage_repo"))
    if not isinstance(repo, dict) or not repo.get("full_name"):
        raise ValueError(t("err.repo_unavailable"))
    from urllib.parse import quote
    release_path = "/releases/tags/" + quote(source["tag"], safe="") if source.get("tag") else "/releases/latest"
    release = github_api_get("https://api.github.com/repos/" + repo["full_name"] + release_path, verify, t("gh.stage_release_one"))
    if not isinstance(release, dict):
        raise ValueError(t("err.no_release"))
    assets = detect_assets(release.get("assets") or [], repo["full_name"])
    if source.get("asset"):
        assets = [a for a in assets if a["name"] == source["asset"]]
    if not assets:
        raise ValueError(t("err.no_known_asset"))
    return repo, release.get("tag_name") or "", assets


def _prepare_entries(custom_dir: str, text: str, *, insecure: bool = False, replace_target: dict | None = None) -> list[tuple[str, dict]]:
    source = parse_source(text)
    prefs = load_preferences(custom_dir)
    if source["kind"] == "fixed":
        filename = source["asset"]
        if not _extension(filename):
            filename = input(t("cc.filename")).strip()
            if not filename:
                return []
        assets = detect_assets([{"name": filename, "browser_download_url": source["url"]}])
        if not assets:
            raise ValueError(t("err.unknown_format"))
        repo, tag = {}, ""
    else:
        repo, tag, assets = inspect_github(source, verify=not insecure)
    if not assets:
        return []
    preferred = preferred_asset_indices(assets, prefs)
    for i, asset in enumerate(assets, 1):
        platforms = "/".join(_platform_label(p) for p in asset["platforms"]) or t("platform.unset")
        hint = t("cc.last_pref") if i - 1 in preferred else ""
        print(t("cc.asset_line", i, asset["name"], platforms, display_term(asset["architecture"]), display_term(asset["package_kind"]), hint))
    if len(assets) == 1:
        indices = [0]
    else:
        default = ",".join(str(i + 1) for i in preferred)
        text = input(t("cc.asset_prompt", _enter_default(default)))
        indices = _select_indices(text.strip() or default, len(assets))
    selected = [(platform, assets[index]) for index in indices for platform in _pick_platforms(assets[index], prefs)]
    if not selected:
        return []
    if replace_target and len(selected) != 1:
        raise ValueError(t("err.one_platform"))
    default_name = repo.get("name") or Path(assets[indices[0]]["name"]).stem
    if replace_target:
        default_name = replace_target["app"]["简介"]
    name = input(t("cc.name", default_name)).strip() or default_name
    default_category = replace_target["app"].get("分类", "自定义") if replace_target else "自定义"
    category = input(t("cc.category", default_category)).strip() or default_category
    entries = []
    for platform, asset in selected:
        if repo:
            entry = make_github_entry(repo["full_name"], tag, asset, platform, name, category)
        else:
            entry = make_fixed_entry(source["url"], platform, name, category, asset["name"])
            entry.update(custom_architecture=asset["architecture"], custom_package_kind=asset["package_kind"])
        if replace_target:
            entry["id"] = replace_target["id"]
            entry["save_subdir"] = entry["id"]
            entry["enabled"] = replace_target["app"].get("enabled", False)
        entries.append((platform, entry))
    return entries


def _confirm_entries(custom_dir: str, entries: list[tuple[str, dict]], *, download=None, dry_run: bool = False, replace_target: dict | None = None) -> int:
    if not entries:
        print(t("common.cancelled"))
        return 0
    # Repeated inputs in a batch update the same proposed variant once.
    entries = list({(p, a["id"]): (p, a) for p, a in entries}.values())
    existing = {(row["platform"], row["id"]) for row in list_entries(custom_dir)}
    print(t("cc.preview"))
    for platform, app in entries:
        duplicate = t("cc.duplicate") if (platform, app["id"]) in existing else ""
        mode = t("cc.mode_github") if app.get("repo_path") else t("cc.mode_fixed")
        print(t("cc.preview_item", app["简介"], _platform_label(platform), app["分类"], duplicate, app["custom_asset_name"], mode))
        print(t("cc.source", app["custom_source"]))
        if app.get("custom_release_tag"):
            print(t("cc.tag", app["custom_release_tag"]))
    action = input(t("cc.confirm")).strip()
    if action not in ("1", "2"):
        print(t("cc.cancel_keep"))
        return 0
    if dry_run:
        print(t("cc.dry_save", len(entries)))
        return 0
    target_key = (replace_target["platform"], replace_target["id"]) if replace_target else None
    save_entries(custom_dir, entries, replace=True, remove_target=target_key)
    platform, first = entries[0]
    save_preferences(custom_dir, {"platform": platform, "architecture": first.get("custom_architecture", ""), "package_kind": first.get("custom_package_kind", "")})
    print(t("cc.saved", len(entries)))
    if action == "2" and download:
        keys = {(p, a["id"]) for p, a in entries}
        return download([row for row in list_entries(custom_dir) if (row["platform"], row["id"]) in keys])
    return 0


def run_add(custom_dir: str, *, source_text: str = "", download=None, dry_run: bool = False, insecure: bool = False, replace_target: dict | None = None) -> int:
    from tools.lookup_github_suggest import GitHubSuggestError
    try:
        text = source_text or input(t("cc.paste")).strip()
        if not text:
            return 0
        entries = _prepare_entries(custom_dir, text, insecure=insecure, replace_target=replace_target)
        return _confirm_entries(custom_dir, entries, download=download, dry_run=dry_run, replace_target=replace_target)
    except (EOFError, KeyboardInterrupt):
        print("\n" + t("common.cancelled"))
        return 0
    except (ValueError, OSError, GitHubSuggestError) as e:
        print(t("cc.not_saved", e))
        return 1


def run_batch(custom_dir: str, *, download=None, dry_run: bool = False, insecure: bool = False) -> int:
    from tools.lookup_github_suggest import GitHubSuggestError
    try:
        print(t("cc.batch_intro"))
        sources = []
        while True:
            line = input("> ").strip()
            if line == "0":
                return 0
            if not line:
                break
            sources.append(line)
        entries = []
        for text in dict.fromkeys(sources):
            print(t("cc.recognized", text))
            entries.extend(_prepare_entries(custom_dir, text, insecure=insecure))
        return _confirm_entries(custom_dir, entries, download=download, dry_run=dry_run)
    except (EOFError, KeyboardInterrupt):
        print(t("cc.batch_cancel"))
        return 0
    except (ValueError, OSError, GitHubSuggestError) as e:
        print(t("cc.batch_fail", e))
        return 1


def run_transfer(custom_dir: str, *, dry_run: bool = False) -> int:
    try:
        action = input(t("cc.transfer")).strip()
        if action == "1":
            filename = input(t("cc.import_path")).strip().strip('"')
            if not filename:
                return 0
            entries = _validated_import(json.loads(Path(filename).read_text(encoding="utf-8")))
            return _confirm_entries(custom_dir, entries, dry_run=dry_run)
        if action == "2":
            default = str(Path(custom_dir).parent / "custom-catalog-export.json")
            filename = input(t("cc.export_path", default)).strip().strip('"') or default
            bundle = export_entries(custom_dir)
            if Path(filename).exists() and input(t("cc.overwrite")).strip().lower() != "y":
                return 0
            if not dry_run:
                _write_json(Path(filename), bundle)
            print(t("cc.dry_nowrite") if dry_run else t("cc.exported", len(bundle["entries"]), filename))
        return 0
    except (EOFError, KeyboardInterrupt):
        print("\n" + t("common.cancelled"))
        return 0
    except (ValueError, OSError) as e:
        print(t("cc.transfer_fail", e))
        return 1


def run_preferences(custom_dir: str, *, dry_run: bool = False) -> int:
    prefs = load_preferences(custom_dir)
    shown = prefs
    if prefs:
        shown = dict(prefs)
        if shown.get("architecture"):
            shown["architecture"] = display_term(shown["architecture"])
        if shown.get("package_kind"):
            shown["package_kind"] = display_term(shown["package_kind"])
        if shown.get("platform"):
            shown["platform"] = _platform_label(shown["platform"])
    print(t("cc.prefs", shown or t("cc.prefs_unset")))
    action = input(t("cc.prefs_menu")).strip()
    if action == "1":
        for i, platform in enumerate(PLATFORMS, 1):
            print("  %d  %s" % (i, _platform_label(platform)))
        indices = _select_indices(input(t("cc.prefs_platform")), len(PLATFORMS))
        if len(indices) != 1:
            return 0
        archs = ("x64", "ARM64", "ARM32", "x86", "通用")
        print(t("cc.arch_prefix") + " / ".join("%d=%s" % (i, display_term(a)) for i, a in enumerate(archs, 1)))
        indices_arch = _select_indices(input(t("cc.prefs_arch")), len(archs))
        kind = input(t("cc.prefs_kind", t("kind.portable"), t("kind.installer"))).strip()
        prefs = {"platform": PLATFORMS[indices[0]], "architecture": archs[indices_arch[0]] if indices_arch else "", "package_kind": {"1": "绿色/便携版", "2": "安装版"}.get(kind, "")}
    elif action == "2":
        prefs = {}
    else:
        return 0
    if not dry_run:
        save_preferences(custom_dir, prefs)
    print(t("cc.dry_nowrite") if dry_run else t("cc.prefs_saved"))
    return 0


def run_manage(custom_dir: str, *, download=None, dry_run: bool = False, insecure: bool = False) -> int:
    try:
        rows = list_entries(custom_dir)
        if not rows:
            print(t("cc.empty"))
            return 0
        for i, row in enumerate(rows, 1):
            print("  %d  %s · %s · %s" % (i, row["app"]["简介"], _platform_label(row["platform"]), display_term(row["app"].get("custom_architecture", ""))))
        indices = _select_indices(input(t("cc.manage_pick")), len(rows))
        if len(indices) != 1:
            return 0
        row = rows[indices[0]]
        action = input(t("cc.manage_action")).strip()
        if action == "2":
            old_source = row["app"].get("custom_source") or row["app"].get("releases_url") or ""
            text = input(t("cc.new_source", old_source)).strip() or old_source
            return run_add(custom_dir, source_text=text, download=download, dry_run=dry_run, insecure=insecure, replace_target=row)
        if action == "1":
            name = input(t("cc.keep_name")).strip() or row["app"]["简介"]
            category = input(t("cc.keep_category")).strip() or row["app"].get("分类", "自定义")
            print(t("cc.will_edit", name, _platform_label(row["platform"]), category))
            if input(t("cc.confirm_edit")).strip().lower() == "y":
                if not dry_run:
                    edit_entry(custom_dir, row["platform"], row["id"], {"简介": name, "分类": category})
                print(t("cc.dry_nowrite") if dry_run else t("cc.edited"))
        elif action == "3":
            print(t("cc.will_delete", row["app"]["简介"]))
            if input(t("cc.confirm_delete")).strip().lower() == "y":
                if not dry_run:
                    delete_entry(custom_dir, row["platform"], row["id"])
                print(t("cc.dry_nodelete") if dry_run else t("cc.deleted"))
        return 0
    except (EOFError, KeyboardInterrupt):
        print("\n" + t("common.cancelled"))
        return 0
    except (ValueError, OSError) as e:
        print(t("cc.not_modified", e))
        return 1


MENU_BACK = object()
MENU_QUIT = object()


def _is_back_command(line: str) -> bool:
    return line == "0" or line.lower() in ("b", "back", "返回")


def _is_quit_command(line: str) -> bool:
    return line.lower() == "q"


def run_menu(custom_dir: str, *, search, download, dry_run: bool = False, insecure: bool = False, nested: bool = False) -> int | object:
    """直接进入时选完即返回，0 退出。从清单进入（nested）时保持菜单，直到返回上一级。"""
    while True:
        try:
            print(t("cc.menu"))
            action = input(t("cc.choose")).strip()
            if _is_quit_command(action):
                print(t("common.quit"))
                return 0
            if _is_back_command(action):
                return MENU_BACK if nested else 0
            if action == "1":
                query = input(t("cc.keyword_cancel")).strip()
                code = search(query) if query else 0
            elif action == "2":
                code = run_add(custom_dir, download=download, dry_run=dry_run, insecure=insecure)
            elif action == "3":
                code = run_manage(custom_dir, download=download, dry_run=dry_run, insecure=insecure)
            elif action == "4":
                code = run_batch(custom_dir, download=download, dry_run=dry_run, insecure=insecure)
            elif action == "5":
                code = run_transfer(custom_dir, dry_run=dry_run)
            elif action == "6":
                if input(t("cc.undo_ask")).strip().lower() == "y":
                    if dry_run:
                        print(t("cc.dry_noundo"))
                    else:
                        print(t("cc.restored") if undo_last_change(custom_dir) else t("cc.nothing_undo"))
                code = 0
            elif action == "7":
                code = run_preferences(custom_dir, dry_run=dry_run)
            else:
                if nested:
                    print(t("common.invalid_choice"))
                    continue
                return 0
            if code is MENU_QUIT:
                return 0
            if not nested:
                return int(code or 0)
        except (EOFError, KeyboardInterrupt):
            print("\n" + t("common.cancelled"))
            return 0
        except (ValueError, OSError) as e:
            print(t("cc.not_modified", e))
            if not nested:
                return 1
