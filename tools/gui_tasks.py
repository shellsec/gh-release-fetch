"""Task dispatch for the Windows download queue."""
from pathlib import Path
from tempfile import TemporaryDirectory
import re
import sys
from urllib.parse import quote, unquote, urlsplit
import webbrowser

import auto_update
from tools import chrome_store, repository_download as repository
from tools.download_engine import available_target, check_pause, download, download_url


def extract_links(text):
    """Extract download inputs from prose in their first-seen order."""
    text = re.sub(r"\\([:/])", r"\1", text)
    pattern = r"""https?://[^\s<>"'`，。；：！？、（）【】《》]+|(?<![\w/])catalog:[a-z_]+/[^\s<>"'`，。；：！？、（）【】《》]+"""
    found = {}
    for match in re.finditer(pattern, text, re.IGNORECASE):
        value = match[0].rstrip(".,;!?]}")
        while value.endswith(")") and value.count(")") > value.count("("):
            value = value[:-1]
        try:
            address = urlsplit(value)
            if address.scheme in ("http", "https") and (not address.hostname or address.username):
                continue
            if address.hostname == "github.com" and address.scheme == "https":
                parts = address.path.strip("/").split("/")
                if len(parts) >= 2 and (len(parts) == 2 or parts[2] in ("blob", "issues", "pull", "wiki", "releases")):
                    root = f"https://github.com/{parts[0]}/{parts[1].removesuffix('.git')}"
                    repository.parse_repository(root)
                    if len(parts) < 4 or parts[2] != "releases":
                        value = root
                key = value.casefold() if value.count("/") == 4 else value
            else:
                chrome = chrome_store.extension_id(value)
                if chrome:
                    value = chrome_store.store_url(chrome)
                key = value
        except ValueError:
            continue
        found.setdefault(key, value)
    if not found:
        for value in text.split():
            if chrome_store.EXTENSION_ID.fullmatch(value) or re.fullmatch(r"[\w.-]+/[\w.-]+", value, re.ASCII):
                found.setdefault(value, value)
    return list(found.values())


def release_assets(source, ref):
    parsed = repository.parse_repository(source)
    tag = ref or parsed["ref"]
    release = repository.api(parsed["repo"] + "/releases/" + ("tags/" + quote(tag, safe="") if tag else "latest"))
    assets = [asset for asset in release.get("assets", []) if not parsed["asset"] or asset["name"] == parsed["asset"]]
    return [(a["name"], a["browser_download_url"]) for a in assets]


def catalog_assets(app, platform):
    """Return the catalog default and selectable files without downloading them."""
    repo = app.get("repo_path")
    special = (app.get("fixed_download_url") or auto_update.uses_github_pages_manifest(app)
               or auto_update.uses_go_dev_json(app) or auto_update.uses_docker_desktop(app))
    if repo and not special:
        tag = auto_update.pinned_release_tag(app)
        release = repository.api(repo + "/releases/" + ("tags/" + quote(tag, safe="") if tag else "latest"))
        version = release["tag_name"]
        files = [asset for asset in release.get("assets", []) if asset.get("name") and asset.get("browser_download_url")]
        defaults = [a for a in files if auto_update.asset_targets_app(a["name"], a["browser_download_url"], app)]
        extensions = (".exe", ".msi", ".msix", ".dmg", ".pkg", ".apk", ".ipa", ".appimage",
                      ".deb", ".rpm", ".zip", ".7z", ".tar.gz", ".tar.xz", ".nro")
        choices = [a for a in files if a in defaults or a["name"].lower().endswith(extensions)]
        return version, choices, defaults[0]["browser_download_url"] if defaults else None
    with TemporaryDirectory() as folder:
        version, url = auto_update.check_latest_version(app, str(Path(folder) / "release.html"), platform_key=platform)
    if not url:
        return version, [], None
    name = unquote(urlsplit(url).path.rsplit("/", 1)[-1])
    return version, [{"name": name, "browser_download_url": url}], url


def execute(task, root, report, cancelled, resolved=lambda _: None, save_target=lambda _: None,
            on_status=None):
    check_pause(cancelled)
    output = Path(task["output"])
    threads = task["threads"]
    transfer = dict(report=report, cancelled=cancelled)
    kind = task["kind"]

    def destination(path):
        previous = task.get("reserved_target")
        candidate = Path(previous) if previous else Path(path)
        if not previous or candidate.exists():
            candidate = available_target(candidate)
        save_target(str(candidate))
        return candidate

    if kind == "direct":
        transfer["on_status"] = on_status
        url = task["source"]
        parsed = urlsplit(url)
        if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username is not None:
            raise ValueError("请输入 HTTP(S) 文件地址")
        filename = repository.safe_name(unquote(parsed.path.rsplit("/", 1)[-1]) or "download")
        target = destination(task.get("target") or output / filename)
        if parsed.scheme == "https" and not parsed.query and parsed.netloc.lower() in (
            "github.com", "codeload.github.com", "raw.githubusercontent.com"
        ):
            result = download(url, target, route=task.get("route", "auto"), threads=threads, **transfer)
        else:
            if on_status:
                on_status("route", "direct")
            result = download_url(url, target, threads=threads, **transfer)
        return repository.extract_zip(result) if task.get("extract") else result
    if kind == "page":
        if not webbrowser.open(task["source"]):
            raise OSError("无法启动默认浏览器")
        return None
    if kind == "crx":
        target = Path(task["target"]) if task.get("target") else (output / "chrome" if task.get("catalog") else output) / (task["source"] + ".crx")
        if target.is_file():
            try:
                chrome_store.validate_crx(target)
            except (OSError, ValueError):
                pass
            else:
                return target
        target = destination(target)
        return chrome_store.download_crx(task["source"], target, threads=threads, **transfer)
    if kind == "catalog":
        platform = task["platform"]
        directory = task["directory"]
        # Queued tasks retain the snapshot selected when they were added.
        source = task.get("catalog_root") or (root if directory == "apps-custom" else getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
        cfg = auto_update.load_config(apps_dir=str(Path(source) / directory), only_platforms=[platform])
        apps = auto_update.select_apps(cfg, [task["source"]], platform)
        if len(apps) != 1:
            raise ValueError("目录中找不到该条目")
        cfg = dict(cfg, download_subdir_by_platform=True)
        selected = task.get("catalog_asset")
        return auto_update.update_one(
            apps[0], str(output), verify=auto_update.resolve_tls_verify(cfg, False),
            platform_key=platform, cfg=cfg, download_only=True,
            transfer=dict(transfer, threads=threads, resolved=resolved, destination=destination),
            selected_asset=selected,
        )
    source = task["source"]
    if kind == "release-latest":
        from tools.custom_catalog import filename_pattern
        import re

        parsed = repository.parse_repository(source)
        if not parsed["asset"]:
            raise ValueError("历史缺少原附件名，请在链接下载中重新选择")
        assets = release_assets(parsed["repo"], "")
        pattern = filename_pattern(parsed["asset"], parsed["ref"])
        matches = [url for name, url in assets if re.fullmatch(pattern, name, re.IGNORECASE)]
        if len(matches) != 1:
            raise ValueError("最新版没有唯一对应附件，请在链接下载中重新选择")
        source, kind = matches[0], "release"
    return repository.run(
        source=source, kind=kind, ref=task.get("ref", ""),
        output=task.get("target"), route=task.get("route", "auto"), threads=threads,
        shallow=task.get("shallow", False), submodules=task.get("submodules", False),
        lfs=task.get("lfs", False), extract=task.get("extract", False),
        interactive=False, base_dir=root, transfer=dict(transfer, resolved=resolved, destination=destination),
        download_dir=output / "repository",
    )
