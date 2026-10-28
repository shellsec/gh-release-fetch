#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
在 apps/ 配置中模糊查找应用，显示分片与分类，并可交互开启 enabled / 加入更新列表。

用法：
  python lookup_app.py drawio
  python lookup_app.py --platform windows cherrytree
  python lookup_app.py --apps-dir apps-mobile --platform android termux
  python lookup_app.py --apps-dir VibeCodingToolsDown warp
  python lookup_app.py --yes drawio          # 匹配项全部开启，不询问
  python lookup_app.py --dry-run drawio      # 只查询，不写文件
  无参数：先选清单。关键词回车回清单；选条目 b/回车回关键词；操作 b/回车回条目。
  下载/启用/加入列表/打开页面做完后仍留在条目列表。q 退出。带参数时关键词回车仍退出。
  Windows 快捷入口：lookup_mobile.bat / lookup_ios.bat / lookup_switch.bat / lookup_ps5.bat

加入更新列表（根目录 saved_apps_<平台>.json，配合 run_saved_apps.bat 一键更新）：
  python lookup_app.py cherrytree            # 交互：1下载 / 2加入并下载 / 3加入列表 / 4启用 / 5打开页面
  python lookup_app.py --save cherrytree     # 选中后可用操作 3 加入列表
  python lookup_app.py -y --download drawio  # 全部匹配项：立刻下载（不改 enabled）
  python lookup_app.py --download termux     # 交互选中后默认操作 1，做完回到条目

本地清单零命中时改为 GitHub 仓库搜索（不先访问 GitHub）：
  只建议一条安装包，回车下载、其它键取消；并列仓库或多个合格包则编号选择。
  交互时取消或完成后回到关键词。--dry-run 只打印；--no-prompt 仅在仓库名一致且只有一个合格包时下载。这两条不进入上述循环。
  --save 才把该仓库以 enabled=false 追加到 apps 分片（拿不准写入 11-工具.json）。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) if not getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(sys.executable))
if not getattr(sys, "frozen", False) and SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from tools.ghrf_runtime import resolve_auto_update_argv  # noqa: E402
from tools.ui_lang import t  # noqa: E402

DEFAULT_APPS_DIR = os.path.join(SCRIPT_DIR, "apps")
DESKTOP_PLATFORMS = ("windows", "darwin", "linux")
SHARD_RE = re.compile(r"^\d+-(.+)\.json$", re.UNICODE)

from tools.app_download import (  # noqa: E402
    is_app_downloadable,
    open_page,
    resolve_open_page_url,
)
from tools.app_list import (  # noqa: E402
    CATALOGS,
    PLATFORMS,
    default_list_basename,
    default_list_path,
    save_hits_by_platform,
)


def _dump(path: str, data) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def platform_keys_for_apps_dir(apps_dir: str) -> tuple[str, ...]:
    root = os.path.join(apps_dir, "root.json")
    if os.path.isfile(root):
        with open(root, encoding="utf-8") as f:
            cfg = json.load(f)
        keys = cfg.get("platform_keys")
        if isinstance(keys, list) and keys:
            return tuple(str(k) for k in keys)
    return DESKTOP_PLATFORMS


def discover_shard_files(apps_dir: str) -> list[tuple[str, str]]:
    """返回 [(platform, abspath), ...]"""
    out: list[tuple[str, str]] = []
    for plat in platform_keys_for_apps_dir(apps_dir):
        sub = os.path.join(apps_dir, plat)
        if os.path.isdir(sub):
            for name in sorted(os.listdir(sub)):
                if name.endswith(".json"):
                    out.append((plat, os.path.join(sub, name)))
            continue
        single = os.path.join(apps_dir, "%s.json" % plat)
        if os.path.isfile(single):
            out.append((plat, single))
    return out


def shard_label_from_filename(filename: str) -> str:
    m = SHARD_RE.match(filename)
    return m.group(1) if m else ""


def load_apps_array(abspath: str) -> list:
    with open(abspath, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "apps" in data:
        data = data["apps"]
    if not isinstance(data, list):
        raise ValueError("%s：必须是 JSON 数组" % abspath)
    return data


def match_score(query: str, app: dict) -> int:
    q = query.strip().lower()
    if not q:
        return 0
    parts = [q]
    if " " in q:
        parts.extend(p for p in q.split() if p)

    best = 0
    idv = (app.get("id") or "").lower()
    fields = [
        idv,
        (app.get("简介") or "").lower(),
        (app.get("分类") or "").lower(),
        (app.get("repo_path") or "").lower(),
        (app.get("releases_url") or "").lower(),
        (app.get("url_hint") or "").lower(),
    ]
    aliases = app.get("aliases") or []
    if isinstance(aliases, str):
        aliases = [aliases]
    for alias in aliases:
        fields.append(str(alias).lower())
    for token in parts:
        if idv == token:
            best = max(best, 100)
        elif idv.startswith(token):
            best = max(best, 80)
        elif token in idv:
            best = max(best, 60)
        for text in fields[1:]:
            if token in text:
                best = max(best, 40)
    return best


def search_apps(apps_dir: str, query: str, min_score: int = 40) -> list[dict]:
    hits: list[dict] = []
    for platform, abspath in discover_shard_files(apps_dir):
        rel = os.path.relpath(abspath, apps_dir).replace("\\", "/")
        shard_name = os.path.basename(abspath)
        shard_cat = shard_label_from_filename(shard_name)
        try:
            items = load_apps_array(abspath)
        except (OSError, json.JSONDecodeError, ValueError) as e:
            print(t("common.warn_skip", rel, e), file=sys.stderr)
            continue
        for app in items:
            if not isinstance(app, dict):
                continue
            score = match_score(query, app)
            if score < min_score:
                continue
            cat = (app.get("分类") or "").strip() or shard_cat or "(未填分类)"
            hits.append(
                {
                    "score": score,
                    "platform": platform,
                    "path": rel,
                    "abspath": abspath,
                    "apps_dir": apps_dir,
                    "shard": shard_name,
                    "shard_category": shard_cat,
                    "id": (app.get("id") or "").strip(),
                    "分类": cat,
                    "enabled": app.get("enabled") is True,
                    "简介": (app.get("简介") or "").strip(),
                    "repo_path": (app.get("repo_path") or "").strip(),
                    "downloadable": is_app_downloadable(app),
                    "open_page_url": resolve_open_page_url(app),
                }
            )
    hits.sort(key=lambda h: (-h["score"], h["platform"], h["id"]))
    return hits


def print_hits(hits: list[dict]) -> None:
    print()
    print(t("hits.count", len(hits)))
    print("-" * 72)
    for i, h in enumerate(hits, 1):
        en = t("hits.yes") if h["enabled"] else t("hits.no")
        brief = h["简介"]
        if len(brief) > 56:
            brief = brief[:53] + "..."
        mode = t("hits.downloadable") if h.get("downloadable") else t("hits.page_only")
        print("[%d] %s  id=%s  enabled=%s  [%s]" % (i, h["platform"], h["id"], en, mode))
        print(t("hits.shard", h["path"]))
        print(t("hits.category", h["分类"]))
        if h["repo_path"]:
            print(t("hits.repo", h["repo_path"]))
        if (not h.get("downloadable")) and (h.get("open_page_url") or "").strip():
            print(t("hits.page", h["open_page_url"].strip()))
        if brief:
            print(t("hits.brief", brief))
        print()


def set_enabled_in_file(abspath: str, app_id: str, enabled: bool) -> bool:
    items = load_apps_array(abspath)
    changed = False
    for app in items:
        if isinstance(app, dict) and (app.get("id") or "").strip() == app_id:
            if app.get("enabled") is enabled:
                continue
            app["enabled"] = enabled
            changed = True
    if changed:
        _dump(abspath, items)
    return changed


_BACK = object()
_QUIT = object()


def _is_back_command(line: str) -> bool:
    return line == "0" or line.lower() in ("b", "back", "返回")


def _is_quit_command(line: str) -> bool:
    return line.lower() == "q"


def prompt_choose_hits(hits: list[dict]) -> list[dict] | object:
    """勾选序号。b/回车返回关键词，q 退出。取消时返回空列表。"""
    if not hits:
        return []
    while True:
        print(t("choose.title"))
        print(t("choose.hint"))
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n" + t("common.cancelled"))
            return []
        if line and _is_quit_command(line):
            print(t("common.quit"))
            return _QUIT
        if not line or _is_back_command(line):
            return _BACK
        if line.lower() in ("a", "all", "*"):
            return list(hits)
        indices: list[int] = []
        invalid = False
        for part in line.replace("，", ",").split(","):
            part = part.strip()
            if not part:
                continue
            if not part.isdigit():
                print(t("common.invalid_input", part))
                invalid = True
                break
            idx = int(part)
            if idx < 1 or idx > len(hits):
                print(t("common.index_range", idx))
                invalid = True
                break
            indices.append(idx - 1)
        if invalid or not indices:
            if not invalid:
                print(t("common.invalid_input", line))
            continue
        return [hits[i] for i in sorted(set(indices))]


def apply_enable(chosen: list[dict], dry_run: bool) -> int:
    """对 chosen 开启 enabled，返回成功条数。"""
    n = 0
    for h in chosen:
        if h["enabled"]:
            print(t("enable.skip", h["platform"], h["id"]))
            continue
        if dry_run:
            print(t("enable.dry", h["platform"], h["id"], h["path"]))
            n += 1
            continue
        if set_enabled_in_file(h["abspath"], h["id"], True):
            h["enabled"] = True
            print(t("enable.done", h["platform"], h["id"], h["path"]))
            n += 1
        else:
            print(t("enable.missing", h["path"], h["id"]))
    return n


def prompt_yes_no(question: str, default_no: bool = True) -> bool:
    try:
        line = input(question).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\n" + t("common.cancelled"))
        return False
    if not line:
        return not default_no
    return line in ("y", "yes", "是", "1")


def _list_files_hint(chosen: list[dict]) -> str:
    plats = sorted({h["platform"] for h in chosen})
    names = [default_list_basename(p) for p in plats]
    return "、".join(names)


def prompt_add_to_saved_list(
    chosen: list[dict],
    apps_dir: str,
    dry_run: bool,
    *,
    auto: bool = False,
    save_path: str | None = None,
) -> bool:
    """询问是否加入根目录更新列表。"""
    if not chosen:
        return False
    hint = save_path or _list_files_hint(chosen)
    if not auto:
        print()
        print(t("save.ask", hint))
        print(t("save.hint"))
        if not prompt_yes_no("> "):
            print(t("save.skip"))
            return False
    if dry_run:
        for h in chosen:
            print(t("save.dry", h["platform"], h["id"]))
        return True
    save_hits_by_platform(
        SCRIPT_DIR,
        chosen,
        apps_dir,
        merge=True,
        explicit_path=save_path,
    )
    return True


def prompt_action_mode() -> str | None:
    """1 下载 | 2 加入并下载 | 3 加入列表 | 4 启用 | 5 打开页面 | b/回车返回条目 | q 退出。"""
    while True:
        print()
        print(t("action.title"))
        print(t("action.1"))
        print(t("action.2"))
        print(t("action.3"))
        print(t("action.4"))
        print(t("action.5"))
        print(t("action.nav"))
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n" + t("common.cancelled"))
            return None
        if line and _is_quit_command(line):
            print(t("common.quit"))
            return "quit"
        if not line or _is_back_command(line):
            return "back"
        if line in ("1", "2", "3", "4", "5"):
            return line
        low = line.lower()
        if low in ("d", "download", "下载", "down"):
            return "1"
        if low in ("o", "open", "打开", "页面", "url"):
            return "5"
        if low in ("sd", "save-download", "加入下载", "列表下载"):
            return "2"
        if low in ("s", "save", "list", "列表", "加入"):
            return "3"
        if low in ("e", "enable", "启用", "on"):
            return "4"
        print(t("action.invalid", line))


def run_open_pages(chosen: list[dict], dry_run: bool) -> int:
    """在浏览器中打开条目对应页面。"""
    if not chosen:
        return 0
    opened = 0
    for h in chosen:
        url = (h.get("open_page_url") or "").strip()
        if not url:
            print(t("open.skip", h["platform"], h["id"]))
            continue
        print()
        if dry_run:
            print(t("open.dry", url, h["platform"], h["id"]))
            opened += 1
            continue
        if open_page(url):
            print(t("open.done", h["platform"], h["id"], url))
            opened += 1
        else:
            print(t("open.fail", url))
    return 0 if opened else 1


def _apps_dir_cli_args(apps_dir: str) -> list[str]:
    if os.path.normpath(apps_dir) == os.path.normpath(DEFAULT_APPS_DIR):
        return []
    try:
        rel = os.path.relpath(apps_dir, SCRIPT_DIR)
        if not rel.startswith(".."):
            return ["--apps-dir", rel]
    except ValueError:
        pass
    return ["--apps-dir", apps_dir]


def run_download_now(
    chosen: list[dict],
    apps_dir: str,
    dry_run: bool,
    *,
    insecure: bool = False,
) -> int:
    """按 id 调用 auto_update 下载；不可下载条目改为打开页面。"""
    page_only = [h for h in chosen if not h.get("downloadable")]
    downloadable = [h for h in chosen if h.get("downloadable")]
    if page_only:
        print(t("download.page_only", len(page_only)))
        run_open_pages(page_only, dry_run)
    if not downloadable:
        if page_only:
            return 0
        print(t("download.none"))
        return 1

    by_plat: dict[tuple[str, str], list[str]] = {}
    for h in downloadable:
        by_plat.setdefault((h.get("apps_dir", apps_dir), h["platform"]), []).append(h["id"])

    exit_code = 0
    for (source_dir, plat), ids in sorted(by_plat.items()):
        extra = _apps_dir_cli_args(source_dir)
        if insecure:
            extra.append("--insecure")
        ids = sorted(set(ids))
        cmd = resolve_auto_update_argv(
            SCRIPT_DIR, ["--platform", plat, *extra, *ids]
        )
        print()
        print(t("download.banner", plat, ", ".join(ids)))
        if dry_run:
            print(t("download.dry", " ".join(cmd)))
            continue
        r = subprocess.run(cmd, cwd=SCRIPT_DIR)
        if r.returncode != 0:
            exit_code = r.returncode
    return exit_code


def run_interactive(
    hits: list[dict],
    apps_dir: str,
    dry_run: bool,
    *,
    save_path: str | None = None,
    prefer_download: bool = False,
    insecure: bool = False,
) -> int | object:
    while True:
        chosen = prompt_choose_hits(hits)
        if chosen is _BACK:
            return _BACK
        if chosen is _QUIT:
            return _QUIT
        if not chosen:
            return 0

        print(t("action.selected", len(chosen)))

        action: str | None
        if prefer_download:
            action = "1"
            print(t("action.download_flag"))
        else:
            action = prompt_action_mode()
        if action == "quit":
            return _QUIT
        if not action:
            return 0
        if action == "back":
            print_hits(hits)
            continue

        if action == "1":
            run_download_now(chosen, apps_dir, dry_run, insecure=insecure)
        elif action == "5":
            run_open_pages(chosen, dry_run)
        elif action == "2":
            prompt_add_to_saved_list(
                chosen, apps_dir, dry_run, auto=True, save_path=save_path
            )
            run_download_now(chosen, apps_dir, dry_run, insecure=insecure)
        elif action == "3":
            prompt_add_to_saved_list(
                chosen, apps_dir, dry_run, auto=True, save_path=save_path
            )
        elif action == "4":
            n = apply_enable(chosen, dry_run)
            if n:
                print(t("enable.total", n))
            elif all(h["enabled"] for h in chosen):
                print(t("enable.already"))
        print_hits(hits)


def enable_all_matches(hits: list[dict], dry_run: bool) -> int:
    return apply_enable(hits, dry_run)


def prompt_catalog_and_query() -> bool:
    """无参数启动：先选清单，再输入关键词。空关键词回到清单；q 或取消则退出。"""
    if len(sys.argv) > 1:
        return True
    print(t("usage.1"))
    print(t("usage.2"))
    print(t("usage.3"))
    print(t("usage.4"))
    print(t("usage.5"))
    print(t("usage.6"))
    print(t("usage.7"))
    print()
    options = [
        (t("catalog.handheld") if platform == "linux_handheld" else label, ["--apps-dir", directory, "--platform", platform], (platform, *aliases))
        for label, directory, platform, aliases in CATALOGS
    ]
    options.append((t("catalog.custom"), ["--custom"], ("custom", "自定义")))
    options.append((t("catalog.all"), ["--all-catalogs"], ("all", "全部")))
    while True:
        print(t("catalog.which"))
        for index, (label, _, _) in enumerate(options, 1):
            print("  %d  %s" % (index, label))
        try:
            choice = input(t("catalog.prompt", len(options))).strip().lower() or "1"
        except (EOFError, KeyboardInterrupt):
            print("\n" + t("common.cancelled"))
            return False
        if choice == "q":
            print(t("common.quit"))
            return False
        selected = None
        for index, (label, extra, aliases) in enumerate(options, 1):
            if choice == str(index) or choice in aliases:
                selected = (label, extra)
                break
        if selected is None:
            print(t("common.invalid_choice"))
            continue
        label, extra = selected
        print(t("catalog.chosen", label))
        if extra == ["--custom"]:
            sys.argv[1:] = extra
            return True
        try:
            text = input(t("catalog.keyword")).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n" + t("common.cancelled"))
            return False
        if not text:
            continue
        try:
            parts = shlex.split(text, posix=(os.name != "nt"))
        except ValueError as exc:
            print(t("common.invalid_text", exc))
            continue
        if not parts:
            continue
        sys.argv[1:] = extra + parts
        return True


def _prompt_next_query(menu_mode: bool) -> list[str] | object | None:
    """重新输入关键词。菜单模式下空输入返回 _BACK；否则空输入表示退出。"""
    hint = t("catalog.hint_back") if menu_mode else t("catalog.hint_quit")
    while True:
        print()
        print(t("catalog.keyword_again", hint))
        try:
            text = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n" + t("common.cancelled"))
            return None
        if not text:
            return _BACK if menu_mode else None
        try:
            return shlex.split(text, posix=(os.name != "nt"))
        except ValueError as exc:
            print(t("common.invalid_text", exc))


def _stay_in_session(args) -> bool:
    """一次性参数做完即返回，不再问下一个关键词。"""
    return not (args.dry_run or args.no_prompt or args.yes or args.open)


def _resume_query(args, menu_mode: bool) -> int | object | None:
    """再问关键词。None 表示已写回 args.query，调用方继续检索。"""
    print(t("catalog.back_search"))
    nxt = _prompt_next_query(menu_mode)
    if nxt is _BACK:
        return _BACK
    if not nxt:
        return 0
    args.query = nxt
    return None


def main(argv: list[str] | None = None) -> int:
    """无参数时关键词回车回到清单；q 或在清单上取消则退出。"""
    menu_mode = argv is None and len(sys.argv) <= 1
    while True:
        if menu_mode:
            sys.argv = [sys.argv[0]]
            if not prompt_catalog_and_query():
                return 0
        result = _dispatch(None if menu_mode else argv, menu_mode=menu_mode)
        if result is _BACK:
            continue
        if result is _QUIT:
            return 0
        return int(result or 0)


def _dispatch(argv: list[str] | None = None, *, menu_mode: bool = False) -> int | object:
    parser = argparse.ArgumentParser(description="在 apps 配置中模糊查找应用并可开启 enabled")
    parser.add_argument("query", nargs="*", help="关键词（如 drawio、v2ray）")
    parser.add_argument("--all-catalogs", action="store_true", help="搜索全部平台清单")
    custom_group = parser.add_mutually_exclusive_group()
    custom_group.add_argument("--custom", action="store_true", help="自定义软件：搜索、添加、管理")
    custom_group.add_argument("--custom-add", nargs="?", const="", metavar="SOURCE", help="添加 GitHub 仓库 / Release / 固定下载链接；可省略地址后交互输入")
    parser.add_argument(
        "--apps-dir",
        default=DEFAULT_APPS_DIR,
        help="配置根目录（默认项目 apps/）",
    )
    parser.add_argument(
        "--min-score",
        type=int,
        default=40,
        help="最低匹配分（默认 40）",
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="对全部匹配项直接 enabled=true，不交互询问",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只显示结果，不写 JSON、不下载（GitHub 建议时只打印将下载的仓库和文件）",
    )
    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="不交互。本地命中时只查询；GitHub 建议仅在仓库名一致且只有一个合格安装包时直接下载，否则列出结果并返回非 0",
    )
    parser.add_argument(
        "--platform",
        choices=PLATFORMS,
        help="只显示该平台的匹配项",
    )
    parser.add_argument(
        "--download",
        "-d",
        action="store_true",
        help="交互时默认操作 1（立刻下载）；与 -y 联用则对全部匹配项立刻下载（不改 enabled）",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="下载时传给 auto_update.py（跳过 HTTPS 证书校验）",
    )
    parser.add_argument(
        "--save",
        nargs="?",
        const="",
        default=None,
        metavar="FILE",
        help="本地命中：将选中项加入更新列表（默认 saved_apps_<平台>.json）。本地未命中的 GitHub 建议：追加一条 enabled=false 到 apps 分片（不重复 id；--dry-run 不写）",
    )
    parser.add_argument(
        "--no-save-prompt",
        action="store_true",
        help="不询问是否加入更新列表（未指定 --save 时生效）",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="对匹配项打开官网 / GitHub Releases 页面（不下载）",
    )
    args = parser.parse_args(argv)

    if args.custom or args.custom_add is not None:
        from tools.custom_catalog import CUSTOM_DIR, MENU_BACK, MENU_QUIT, run_add, run_menu

        custom_dir = os.path.join(SCRIPT_DIR, CUSTOM_DIR)
        def download_custom(rows):
            return run_download_now(rows, custom_dir, args.dry_run, insecure=args.insecure)

        if args.custom_add is not None:
            return run_add(custom_dir, source_text=args.custom_add, download=download_custom, dry_run=args.dry_run, insecure=args.insecure)
        extra = (["--dry-run"] if args.dry_run else []) + (["--insecure"] if args.insecure else [])

        def search_custom(query: str):
            found = _dispatch(
                ["--apps-dir", custom_dir, *extra, *shlex.split(query, posix=(os.name != "nt"))],
                menu_mode=False,
            )
            if found is _QUIT:
                return MENU_QUIT
            if found is _BACK:
                return 0
            return int(found or 0)

        result = run_menu(
            custom_dir,
            search=search_custom,
            download=download_custom,
            dry_run=args.dry_run,
            insecure=args.insecure,
            nested=menu_mode,
        )
        if result is MENU_BACK:
            return _BACK
        return result

    if not args.query:
        from tools.ghrf_runtime import prompt_cli_line

        text = prompt_cli_line([], t("catalog.query_prompt"))
        if not text:
            return 0
        args.query = shlex.split(text, posix=(os.name != "nt"))
    if not args.query:
        print(t("catalog.err_query"), file=sys.stderr)
        return 1

    apps_dir = args.apps_dir
    if not os.path.isabs(apps_dir):
        apps_dir = os.path.normpath(os.path.join(SCRIPT_DIR, apps_dir))
    if not os.path.isdir(apps_dir):
        print(t("catalog.err_dir", apps_dir), file=sys.stderr)
        return 1

    save_path: str | None = None
    if args.save is not None:
        if args.save:
            save_path = args.save if os.path.isabs(args.save) else os.path.join(SCRIPT_DIR, args.save)
        elif args.platform:
            save_path = default_list_path(SCRIPT_DIR, args.platform)

    while True:
        query = " ".join(args.query).strip()

        print(t("catalog.searching", query, t("catalog.all_platforms") if args.all_catalogs else apps_dir))
        if args.all_catalogs:
            hits = []
            for name in (*dict.fromkeys(row[1] for row in CATALOGS), "apps-custom"):
                source_dir = os.path.join(SCRIPT_DIR, name)
                if os.path.isdir(source_dir):
                    hits.extend(search_apps(source_dir, query, min_score=args.min_score))
            hits.sort(key=lambda h: (-h["score"], h["platform"], h["id"]))
        else:
            hits = search_apps(apps_dir, query, min_score=args.min_score)
        if args.platform:
            hits = [h for h in hits if h["platform"] == args.platform]
        if not hits:
            if os.path.basename(apps_dir) == "apps-custom" and not args.all_catalogs:
                print(t("catalog.custom_miss"))
                if not _stay_in_session(args):
                    return 0
                resumed = _resume_query(args, menu_mode)
                if resumed is not None:
                    return resumed
                continue
            from tools.lookup_github_suggest import run_github_suggest

            code = run_github_suggest(
                query=query,
                apps_dir=apps_dir,
                platform=args.platform,
                dry_run=args.dry_run,
                no_prompt=args.no_prompt,
                save=args.save is not None,
                insecure=args.insecure,
            )
            if not _stay_in_session(args):
                return code
            resumed = _resume_query(args, menu_mode)
            if resumed is not None:
                return resumed
            continue

        print_hits(hits)

        if args.open:
            return run_open_pages(hits, args.dry_run)

        if args.no_prompt:
            if args.download:
                return run_download_now(hits, apps_dir, args.dry_run, insecure=args.insecure)
            if args.save is not None:
                prompt_add_to_saved_list(
                    hits, apps_dir, args.dry_run, auto=True, save_path=save_path
                )
            return 0

        if args.yes:
            exit_code = 0
            if args.download:
                exit_code = run_download_now(hits, apps_dir, args.dry_run, insecure=args.insecure)
            else:
                n = enable_all_matches(hits, args.dry_run)
                if n:
                    print(t("enable.total_nl", n))
            if args.save is not None and not args.download:
                prompt_add_to_saved_list(
                    hits, apps_dir, args.dry_run, auto=True, save_path=save_path
                )
            elif not args.no_save_prompt and not args.download:
                prompt_add_to_saved_list(hits, apps_dir, args.dry_run, auto=False)
            return exit_code

        result = run_interactive(
            hits,
            apps_dir,
            args.dry_run,
            save_path=save_path,
            prefer_download=args.download,
            insecure=args.insecure,
        )
        if result is not _BACK:
            return result
        resumed = _resume_query(args, menu_mode)
        if resumed is not None:
            return resumed


if __name__ == "__main__":
    from tools.ghrf_runtime import run_cli
    sys.exit(run_cli(main))
