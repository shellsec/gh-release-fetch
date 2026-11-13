"""One repository entry for release files, source snapshots and Git clones."""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import quote, unquote, urlparse
import webbrowser
import zipfile

import requests
from bs4 import BeautifulSoup

from tools.download_engine import DownloadPaused, ROUTES, atomic_json, download
from tools import chrome_store


class Cancelled(Exception):
    pass


class QuitRequested(Exception):
    pass


MENU_QUIT = object()


def ask(prompt, default=""):
    try:
        value = input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        raise Cancelled() from None
    if value.lower() == "q":
        raise QuitRequested()
    if value.lower() == "b":
        raise Cancelled()
    return value or default


def choose(prompt, items):
    for index, label in enumerate(items, 1):
        print(f"  {index}  {label}")
    while True:
        value = ask(prompt + " [1，b=返回，q=退出]：", "1")
        if value.isdigit() and 1 <= int(value) <= len(items):
            return int(value) - 1
        print("无效选择。")


def parse_repository(text):
    text = text.strip()
    if re.fullmatch(r"[\w.-]+/[\w.-]+", text, re.ASCII):
        text = "https://github.com/" + text
    parsed = urlparse(text)
    if parsed.scheme != "https" or parsed.netloc.lower() != "github.com" or parsed.query or parsed.fragment:
        raise ValueError("请输入 owner/repo 或 HTTPS GitHub 仓库地址")
    parts = parsed.path.strip("/").split("/")
    if len(parts) < 2:
        raise ValueError("缺少作者或仓库名")
    owner, repo = parts[:2]
    repo = repo.removesuffix(".git")
    if not all(re.fullmatch(r"[A-Za-z0-9_.-]+", item) and item not in (".", "..") for item in (owner, repo)):
        raise ValueError("无效仓库名")
    tail = parts[2:]
    result = dict(repo=f"{owner}/{repo}", ref="", kind="", asset="", tree=False)
    if not tail or tail == ["releases"] or tail == ["releases", "latest"]:
        return result
    if tail[0] in ("tree", "commit") and len(tail) > 1:
        result.update(kind="source", ref=unquote("/".join(tail[1:])), tree=tail[0] == "tree")
    elif len(tail) > 2 and tail[:2] == ["releases", "tag"]:
        result.update(kind="release", ref=unquote("/".join(tail[2:])))
    elif len(tail) > 3 and tail[:2] == ["releases", "download"]:
        result.update(kind="release", ref=unquote("/".join(tail[2:-1])), asset=unquote(tail[-1]))
    elif len(tail) == 4 and tail[:3] == ["releases", "latest", "download"]:
        result.update(kind="release", asset=unquote(tail[-1]))
    else:
        raise ValueError("支持仓库、tree 分支、commit、Release 页面或附件地址")
    return result


def api(path):
    # Metadata and credentials stay on the official API; no proxy receives tokens.
    with requests.get("https://api.github.com/repos/" + path,
                      headers={"Accept": "application/vnd.github+json", "User-Agent": "GH-Release-Fetch"},
                      timeout=(8, 25)) as response:
        if response.status_code in (403, 429):
            print("GitHub API 限流或拒绝访问，改用官方网页。")
            return github_page_metadata(path)
        response.raise_for_status()
        return response.json()


def github_page_metadata(path):
    owner, name, *tail = path.split("/")
    repo = f"{owner}/{name}"
    base = f"https://github.com/{repo}"
    if tail[:1] == ["releases"]:
        target = base + "/" + "/".join(tail)
        response = requests.get(target, timeout=(8, 25))
        response.raise_for_status()
        parsed = urlparse(response.url)
        prefix = f"/{repo}/releases/tag/"
        if parsed.netloc.lower() != "github.com" or not parsed.path.lower().startswith(prefix.lower()):
            response.status_code = 404
            raise requests.HTTPError("没有正式发布", response=response)
        tag = unquote(parsed.path[len(prefix):])
        response = requests.get(f"{base}/releases/expanded_assets/{quote(tag, safe='')}", timeout=(8, 25))
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        assets = []
        asset_prefix = f"/{repo}/releases/download/{tag}/".casefold()
        for link in soup.select("a[href]"):
            href = link["href"]
            if not unquote(href).casefold().startswith(asset_prefix):
                continue
            row = link.find_parent("li")
            digest = row.select_one('clipboard-copy[value^="sha256:"]') if row else None
            assets.append({"name": unquote(href.rsplit("/", 1)[-1]),
                           "browser_download_url": "https://github.com" + href,
                           "digest": digest["value"] if digest else None})
        return {"tag_name": tag, "assets": assets}

    target = base if not tail else f"{base}/commit/{tail[1]}"
    response = requests.get(target, timeout=(8, 25))
    response.raise_for_status()
    script = BeautifulSoup(response.content, "html.parser").select_one('script[data-target="react-app.embeddedData"]')
    payload = json.loads(script.get_text())["payload"] if script else {}
    info = payload.get("codeViewRepoRoute", {}).get("refInfo", {})
    if tail:
        sha = payload.get("commitRoute", {}).get("commit", {}).get("oid", "")
        if re.fullmatch(r"[a-f0-9]{40}", sha):
            return {"sha": sha}
    if not tail and info.get("name"):
        return {"full_name": repo, "default_branch": info["name"]}
    raise ValueError("无法从 GitHub 网页读取仓库分支或提交")


def resolve_commit(repo, ref, tree=False):
    # A tree URL may include a directory and branches themselves may contain '/'.
    candidates = [ref]
    if tree:
        pieces = ref.split("/")
        candidates = ["/".join(pieces[:i]) for i in range(len(pieces), 0, -1)]
    for candidate in candidates:
        try:
            data = api(f"{repo}/commits/{quote(candidate, safe='')}")
            return data["sha"], candidate
        except requests.HTTPError as exc:
            if exc.response.status_code not in (404, 422):
                raise
    raise ValueError("找不到指定分支、标签或提交")


def safe_name(name):
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name).rstrip(". ")
    if not name or name in (".", ".."):
        raise ValueError("无效文件名")
    if name.split(".")[0].upper() in {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}:
        name = "_" + name
    return name


def validate_zip(path):
    try:
        with zipfile.ZipFile(path) as archive:
            bad = archive.testzip()
            if bad:
                raise ValueError(f"ZIP 校验失败：{bad}")
    except zipfile.BadZipFile as exc:
        raise ValueError("不是完整 ZIP 文件") from exc


def extract_zip(path):
    target = Path(path).with_suffix("")
    if target.exists():
        raise ValueError(f"解压目录已存在，请另选目录：{target}")
    with zipfile.ZipFile(path) as archive:
        for item in archive.infolist():
            normalized = item.filename.replace("\\", "/")
            if normalized.startswith("/") or any(part in ("..",) or ":" in part for part in normalized.split("/")):
                raise ValueError("压缩包包含不安全路径")
            if (item.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError("压缩包包含符号链接")
        target.mkdir()
        archive.extractall(target)
    children = list(target.iterdir())
    return children[0] if len(children) == 1 and children[0].is_dir() else target


def clone(repo, destination, *, ref="", shallow=False, submodules=False, lfs=False):
    hidden = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}
    if not shutil.which("git"):
        raise ValueError("未找到 Git，请安装 Git 或选择源码 ZIP")
    destination = Path(destination)
    if destination.exists():
        raise ValueError(f"目标目录已存在，请换一个目录：{destination}")
    if lfs:
        subprocess.run(["git", "lfs", "version"], check=True, **hidden)
    command = ["git", "clone"]
    if shallow:
        command += ["--depth", "1"]
    remote = f"https://github.com/{repo}.git"
    branch = bool(ref and subprocess.check_output(
        ["git", "ls-remote", "--heads", remote, "refs/heads/" + ref],
        text=True, encoding="utf-8", **hidden).strip())
    if branch:
        command += ["--branch", ref]
    elif ref:
        command += ["--no-checkout"]
    command += ["--", remote, str(destination)]
    environment = {**os.environ, "GIT_LFS_SKIP_SMUDGE": "1"}
    subprocess.run(command, check=True, env=environment, **hidden)
    if ref and not branch:
        fetch = ["git", "-C", str(destination), "fetch"]
        if shallow:
            fetch += ["--depth", "1"]
        subprocess.run([*fetch, "--", "origin", ref], check=True, env=environment, **hidden)
        subprocess.run(["git", "-C", str(destination), "checkout", "--detach", "FETCH_HEAD"], check=True, env=environment, **hidden)
    if submodules:
        subprocess.run(["git", "-C", str(destination), "submodule", "update", "--init", "--recursive"], check=True, env=environment, **hidden)
    if lfs:
        subprocess.run(["git", "-C", str(destination), "lfs", "pull"], check=True, **hidden)
    return destination


def record(directory, task):
    history = Path(directory) / "repository_tasks.json"
    entries = []
    if history.exists():
        entries = json.loads(history.read_text(encoding="utf-8"))
    entries.append({**task, "time": datetime.now(timezone.utc).isoformat()})
    atomic_json(history, entries)


def update_git(path, repo):
    """Update only the expected clean worktree and never discard local changes."""
    path = Path(path).resolve()
    hidden = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}
    def git(*args):
        return subprocess.check_output(["git", "-C", str(path), *args], text=True, encoding="utf-8", **hidden).strip()
    origin = git("remote", "get-url", "origin")
    if origin.removesuffix(".git").rstrip("/") != f"https://github.com/{repo}":
        raise ValueError("远程仓库与任务不一致，请在终端检查")
    if git("status", "--porcelain"):
        raise ValueError("存在本地改动，请先提交或自行暂存，再更新")
    branch = git("symbolic-ref", "--quiet", "--short", "HEAD")
    if not branch:
        raise ValueError("当前处于固定提交，请在终端切换分支后更新")
    subprocess.run(["git", "-C", str(path), "pull", "--ff-only"], check=True, **hidden)


def history_menu(directory, base_dir):
    history = directory / "repository_tasks.json"
    if not history.exists():
        print("暂无仓库下载任务。")
        return 0
    entries = json.loads(history.read_text(encoding="utf-8"))
    entries.reverse()
    task = entries[choose("选择任务", [f"{x['repo']} | {x['kind']} | {x['ref']} | {x['status']}" for x in entries])]
    action = choose("任务操作", ["返回", "打开所在目录", "继续／重新获取", "更新 Git 仓库", "获取最新源码快照"])
    location = task.get("result") or task.get("path")
    path = Path(location) if location else None
    if action == 1:
        if path is None or not path.exists():
            raise ValueError("文件已移动或删除，请重新获取")
        finish_action(1, path, directory)
    elif action in (2, 4):
        latest_ref = task["ref"] if not re.fullmatch(r"[a-fA-F0-9]{7,40}", task["ref"]) else ""
        return run(source=task["repo"], kind="source" if action == 4 else task["kind"],
                   ref=latest_ref if action == 4 else task.get("commit") or task["ref"],
                   output=None if action == 4 else task.get("path"), base_dir=base_dir)
    elif action == 3:
        if task["kind"] != "git" or path is None:
            raise ValueError("该任务不是 Git 克隆，请选择重新获取")
        update_git(path, task["repo"])
        print("Git 更新完成。")
    return 0


def run_chrome(item, *, output, threads, dry_run, interactive, base_dir, download_only=False):
    page = chrome_store.store_url(item)
    target = Path(output).expanduser() if output else Path(base_dir) / "extension_downloads" / f"{item}.crx"
    if dry_run:
        print(json.dumps(dict(extension_id=item, store=page, output=str(target),
                              route="Google", threads=threads), ensure_ascii=False, indent=2))
        return 0
    if interactive:
        if not download_only and choose("Chrome 商店扩展", ["打开商店安装", "下载原版 CRX"]) == 0:
            print(page)
            webbrowser.open(page)
            return 0
        target = Path(ask(f"保存到 [回车={target}]：", str(target))).expanduser()
        threads = (4, 1, 2, 8)[choose("连接数", ["自动（最多 4）", "1", "2", "8"])]
    print("使用线路：Google 官方下载")
    try:
        result = chrome_store.download_crx(item, target, threads=threads)
    except (OSError, ValueError, requests.RequestException) as exc:
        print(f"CRX 下载失败：{exc}\n使用相同扩展 ID、路径和连接数可续传。")
        return 1
    print(f"完成：{result.resolve()}")
    if interactive and choose("完成后操作", ["返回", "打开所在目录"]) == 1:
        finish_action(1, result, target.parent)
    return 0


def run_chrome_batch(items, *, output, threads, dry_run, interactive, base_dir):
    folder = Path(output).expanduser() if output else Path(base_dir) / "extension_downloads"
    if interactive and not dry_run:
        folder = Path(ask(f"批量下载 {len(items)} 个扩展，保存目录 [回车={folder}]：", str(folder))).expanduser()
        threads = (4, 1, 2, 8)[choose("每个文件的连接数", ["自动（最多 4）", "1", "2", "8"])]
    if not dry_run and folder.exists() and not folder.is_dir():
        raise ValueError("批量下载需要目录路径")
    failed = []
    skipped = 0
    for index, item in enumerate(items, 1):
        print(f"[{index}/{len(items)}] {item}")
        target = folder / f"{item}.crx"
        if not dry_run and target.is_file():
            try:
                chrome_store.validate_crx(target)
            except (OSError, ValueError) as exc:
                print(f"已有文件无法校验，请移走后重试：{target}（{exc}）")
                failed.append(item)
            else:
                print(f"已存在，跳过：{target}")
                skipped += 1
            continue
        if run_chrome(item, output=target, threads=threads, dry_run=dry_run,
                      interactive=False, base_dir=base_dir):
            failed.append(item)
    if not dry_run:
        print(f"批量结束：下载 {len(items) - len(failed) - skipped}，跳过 {skipped}，失败 {len(failed)}")
        if failed:
            print("失败项，可重新粘贴重试：" + " ".join(failed))
        if interactive and folder.is_dir() and choose("完成后操作", ["返回", "打开下载目录"]) == 1:
            finish_action(1, folder, folder)
    return int(bool(failed))


def run(*, source="", kind=None, ref="", output=None, route="auto", threads=4,
        shallow=False, submodules=False, lfs=False, extract=False, dry_run=False,
        interactive=True, base_dir=".", catalog_batch=None, catalog_browse=None,
        transfer=None, download_dir=None):
    task = None
    browsed_chrome = False
    browsed_github_extension = False
    directory = Path(base_dir) / "repository_downloads"
    try:
        if not source:
            if not interactive:
                raise ValueError("请提供 GitHub 仓库或 Chrome 商店扩展地址／ID")
            if catalog_browse:
                print("  V  浏览可下载列表")
            source = ask("仓库、Chrome 扩展链接／ID，或粘贴网页下载清单（V=浏览，h=记录，b=返回）：")
            if not source:
                return 0
            if source.lower() == "h":
                return history_menu(directory, base_dir)
            if source.casefold() in ("v", "l") and catalog_browse:
                source, browsed_chrome = catalog_browse()
                browsed_github_extension = not browsed_chrome
        tokens = source.split()
        if catalog_batch and any(token.startswith("catalog:") for token in tokens):
            return catalog_batch(tokens, dry_run=dry_run, output=output)
        if len(tokens) > 1:
            items = [chrome_store.extension_id(token) for token in tokens]
            if not all(items):
                raise ValueError("批量输入只接受 Chrome 扩展详情链接或扩展 ID，用空格分隔")
            return run_chrome_batch(list(dict.fromkeys(items)), output=output, threads=threads,
                                    dry_run=dry_run, interactive=interactive, base_dir=base_dir)
        item = chrome_store.extension_id(source.strip())
        if item:
            return run_chrome(item, output=output, threads=threads, dry_run=dry_run,
                              interactive=interactive, base_dir=base_dir, download_only=browsed_chrome)
        parsed = parse_repository(source)
        repo = parsed["repo"]
        kind = kind or ("source" if parsed["kind"] == "source" else None)
        if not kind:
            kind = ("release", "source", "git")[choose("下载内容", ["发布包（安装使用）", "源码 ZIP（开发阅读）", "Git 克隆（继续开发）"])] if interactive else "release"
        ref = ref or parsed["ref"]
        if dry_run:
            print(json.dumps(dict(repo=repo, kind=kind, ref=ref or "默认版本", output=output,
                                  route=route, threads=threads), ensure_ascii=False, indent=2))
            return 0
        metadata = api(repo)
        print(f"{metadata['full_name']} · {metadata.get('description') or ''}")
        if kind == "release" and interactive and not parsed["asset"]:
            ref = ask(f"Release 标签 [回车={ref or '最新稳定版'}]：", ref)
        if kind != "release" and interactive:
            ref = ask(f"分支／标签／提交 [回车={ref or metadata['default_branch']}]：", ref or metadata["default_branch"])
        directory.mkdir(parents=True, exist_ok=True)
        task = dict(repo=repo, kind=kind, ref=ref, status="failed")
        digest = None
        if kind == "release":
            try:
                release = api(f"{repo}/releases/" + ("tags/" + quote(ref, safe="") if ref else "latest"))
            except requests.HTTPError as exc:
                if exc.response.status_code != 404 or not interactive:
                    raise
                if choose("没有发布包，是否下载源码？", ["下载源码 ZIP", "返回"]) == 1:
                    return 0
                return run(source=repo, kind="source", output=output, route=route, threads=threads,
                           interactive=interactive, base_dir=base_dir)
            assets = [a for a in release.get("assets", []) if not parsed["asset"] or a["name"] == parsed["asset"]]
            if browsed_github_extension:
                chrome_assets = []
                for asset in assets:
                    filename = asset["name"].casefold().replace("_", "-")
                    if re.search(r"\b(?:edge|firefox|source)\b", filename):
                        continue
                    if filename.endswith(".crx") or (
                        filename.endswith(".zip") and re.search(r"\b(?:chrome|chromium)\b", filename)
                    ):
                        chrome_assets.append(asset)
                assets = chrome_assets
            if not assets:
                reason = "该版本没有可识别的 Chrome 发布附件" if browsed_github_extension else "该版本没有发布附件"
                if interactive and not parsed["asset"] and choose(reason, ["下载源码 ZIP", "返回"]) == 0:
                    return run(source=repo, kind="source", ref=release["tag_name"], output=output,
                               route=route, threads=threads, interactive=True, base_dir=base_dir)
                raise ValueError("该 Release 没有匹配附件，请选择源码 ZIP")
            if len(assets) > 1 and not interactive:
                raise ValueError("存在多个附件，请使用附件完整地址或交互选择")
            labels = [f"{a['name']} ({a['size'] / 1048576:.1f} MiB)" if "size" in a else a["name"] for a in assets]
            asset = assets[choose("选择附件", labels)] if len(assets) > 1 else assets[0]
            url, name = asset["browser_download_url"], safe_name(asset["name"])
            digest = asset.get("digest")
            if digest and not digest.startswith("sha256:"):
                digest = None
            task.update(ref=release["tag_name"], asset=asset["name"])
        else:
            sha, resolved_ref = resolve_commit(repo, ref or metadata["default_branch"], parsed["tree"])
            task.update(ref=resolved_ref, commit=sha)
            name = safe_name(repo.replace("/", "-") + "-" + sha[:12])
            if kind == "source":
                url = f"https://github.com/{repo}/archive/{sha}.zip"
                name += ".zip"
        target = Path(output).expanduser() if output else Path(download_dir or directory) / name
        if transfer and transfer.get("destination"):
            target = transfer["destination"](target)
        if interactive:
            target = Path(ask(f"保存到 [回车={target}]：", str(target))).expanduser()
        task["path"] = str(target.resolve())
        if target.exists():
            raise ValueError(f"目标已存在，请换一个路径：{target}")
        if kind == "git":
            target.parent.mkdir(parents=True, exist_ok=True)
            if interactive:
                shallow = choose("历史记录", ["完整历史", "浅克隆（最近一次）"]) == 1
                submodules = choose("子模块", ["不下载", "递归下载"]) == 1
                lfs = choose("Git LFS 文件", ["仅保留指针", "下载实际文件（需要 git-lfs）"]) == 1
            # Preserve a selected branch for future pull; explicit commits/tags stay detached.
            result = clone(repo, target, ref=task["ref"], shallow=shallow, submodules=submodules, lfs=lfs)
            if transfer and transfer.get("resolved"):
                transfer["resolved"](sha)
        else:
            if interactive:
                index = choose("下载线路", ["自动测速选择"] + [name for name, _ in ROUTES])
                route = "auto" if index == 0 else ROUTES[index - 1][0]
                threads = (4, 1, 2, 8)[choose("连接数", ["自动（最多 4）", "1", "2", "8"])]
            options = dict(transfer or {})
            resolved = options.pop("resolved", None)
            options.pop("destination", None)
            result = download(url, target, route=route, threads=threads, digest=digest,
                              validator=validate_zip if kind == "source" else None, **options)
            if resolved:
                resolved(url)
            if kind == "source" and extract:
                result = extract_zip(result)
        completed = task
        task = None
        print(f"完成：{result.resolve()}")
        actions = ["返回", "打开所在目录", "查看任务记录", "打开终端", "用编辑器打开", "查看 README"]
        action = 0
        try:
            if interactive and kind == "source" and not extract:
                # Keep the existing action IDs while putting the default first.
                choices = [1, 6, 0, 2, 3, 4, 5]
                actions.append("解压到同名目录并打开")
                action = choices[choose("完成后操作", [actions[i] for i in choices])]
                if action == 6:
                    try:
                        result = extract_zip(result)
                        print(f"解压完成：{result.resolve()}")
                    except (OSError, ValueError, zipfile.BadZipFile) as exc:
                        print(f"解压失败：{exc}\nZIP 已保存：{result.resolve()}")
                    action = 1
            elif interactive:
                action = choose("完成后操作", actions)
        finally:
            completed.update(status="completed", result=str(result.resolve()))
            record(directory, completed)
        if transfer is not None:
            return result
        if action:
            finish_action(action, result, directory)
        return 0
    except DownloadPaused:
        if task:
            task["status"] = "interrupted"
            record(directory, task)
        raise
    except Cancelled:
        if task:
            task["status"] = "interrupted"
            record(directory, task)
        print("已返回；未完成的下载可用相同输入和下载设置继续。")
        return 0
    except QuitRequested:
        if task:
            task["status"] = "interrupted"
            record(directory, task)
        return MENU_QUIT
    except KeyboardInterrupt:
        if task:
            task["status"] = "interrupted"
            record(directory, task)
        print("\n下载已中断，已保存分片；重新执行相同任务可继续。")
        return 130
    except (OSError, ValueError, RuntimeError, requests.RequestException, subprocess.CalledProcessError, zipfile.BadZipFile) as exc:
        print(f"获取失败：{exc}")
        if task:
            task["error"] = str(exc)
            record(directory, task)
            print("重新选择相同版本和路径可继续下载；Git 失败目录会保留，请检查后换目录重试。")
        if transfer is not None:
            raise
        return 1


def finish_action(action, result, directory, report=print):
    result = Path(result).resolve()
    folder = result if result.is_dir() else result.parent
    if action == 1:
        from auto_update import reveal_in_file_manager
        if not reveal_in_file_manager(str(result)):
            report(f"无法打开所在目录：{folder}")
    elif action == 2:
        history = directory / "repository_tasks.json"
        print(history.read_text(encoding="utf-8"))
    elif action == 3:
        if os.name == "nt":
            subprocess.Popen(["cmd.exe", "/K"], cwd=folder, creationflags=subprocess.CREATE_NEW_CONSOLE)
        elif shutil.which("x-terminal-emulator"):
            subprocess.Popen(["x-terminal-emulator"], cwd=folder)
        elif shutil.which("open"):
            subprocess.Popen(["open", "-a", "Terminal", str(folder)])
        else:
            report(f"请在终端中打开：{folder}")
    elif action == 4:
        editor = shutil.which("code") or shutil.which("codium")
        if os.name == "nt":
            names = ("Code.exe", "VSCodium.exe")
            candidates = [Path(editor).parent.parent / name for name in names] if editor else []
            for variable, subfolder in (("LOCALAPPDATA", "Programs"), ("ProgramFiles", "")):
                base = os.environ.get(variable)
                if base:
                    candidates.extend(Path(base) / subfolder / folder_name / name for folder_name, name in
                                      (("Microsoft VS Code", names[0]), ("VSCodium", names[1])))
            if not editor or Path(editor).suffix.lower() != ".exe":
                editor = next((str(candidate) for candidate in candidates if candidate.is_file()), None)
        if editor:
            subprocess.Popen([editor, str(folder)])
        else:
            report(f"未检测到 VS Code / VSCodium。安装后可用编辑器打开：{folder}")
    elif action == 5:
        readmes = sorted(path for path in folder.glob("[Rr][Ee][Aa][Dd][Mm][Ee]*") if path.is_file())
        if readmes:
            raw = readmes[0].read_bytes()
            if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
                text = raw.decode("utf-16")
            else:
                try:
                    text = raw.decode("utf-8-sig")
                except UnicodeDecodeError:
                    text = raw.decode("gb18030", errors="replace")
            report(text)
        else:
            report(f"当前目录未找到 README，请查看：{folder}")
