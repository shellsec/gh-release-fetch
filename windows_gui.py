"""Windows catalog and persistent download queue."""
from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime
from io import TextIOBase
import json
import os
from pathlib import Path
from queue import Empty, Queue
import sys
from threading import Event, Thread
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from urllib.parse import urlsplit
from uuid import uuid4
import webbrowser

from lookup_app import discover_shard_files, load_apps_array, match_score, shard_label_from_filename
from tools.app_download import is_app_downloadable, resolve_open_page_url
from tools.app_list import CATALOGS
from tools.chrome_store import extension_id, store_url
from tools import catalog_update
from tools.download_engine import DownloadPaused, ROUTES, atomic_json
from tools.ghrf_runtime import repo_root
from tools.repository_download import parse_repository

ROOT = Path(repo_root(__file__))
BASE = Path(getattr(sys, "_MEIPASS", ROOT))
PROFILE = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local" / "share")) / "GHReleaseFetch"
CUSTOM = PROFILE / "apps-custom"
if __name__ == "__main__":
    os.environ["GHRF_CATALOG_PROFILE"] = str(PROFILE)
    os.environ["GHRF_CATALOG_BASE"] = str(BASE)
    PROFILE.mkdir(parents=True, exist_ok=True)

from tools.gui_tasks import execute, extract_links, release_assets
from tools.gui_language import set_language, tr
LABELS = {platform: label for label, _, platform, _ in CATALOGS}
LABELS["linux_handheld"] = "Linux 掌机"
LABELS["chrome"] = "Chrome 扩展"
LABELS["custom"] = "自定义清单"
CATEGORY_ICONS = {
    "AI": "ai", "下载": "download", "云原生": "cloud", "代理与隧道": "network",
    "写作": "writing", "办公": "office", "办公与设计": "design", "设计": "design",
    "加密货币": "finance", "金融与股票": "finance", "可观测": "monitor",
    "网络": "network", "网络与通讯": "network", "浏览器扩展": "chrome",
}
KINDS = {"按链接识别": "", "发布附件": "release", "源码 ZIP": "source", "Git 克隆": "git"}
STATES = {"waiting": "等待", "active": "下载中", "paused": "已暂停", "done": "完成", "failed": "失败"}


def initialize_profile():
    from shutil import copy2

    PROFILE.mkdir(parents=True, exist_ok=True)
    if ROOT != PROFILE and not (PROFILE / ".legacy-imported").exists():
        sources = list(ROOT.glob("saved_apps_*.json"))
        sources.extend((ROOT / "apps-custom").rglob("*.json"))
        sources.extend(ROOT / name for name in ("catalog_downloads/queue.json", "catalog_downloads/settings.json",
                                                "repository_downloads/repository_tasks.json", "update_log.txt",
                                                "catalog_downloads/download.log"))
        for source in sources:
            target = PROFILE / source.relative_to(ROOT)
            if source.is_file() and not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                copy2(source, target)
    if not (CUSTOM / "root.json").exists():
        CUSTOM.mkdir(exist_ok=True)
        atomic_json(CUSTOM / "root.json", {"schema_version": 1})
    if ROOT != PROFILE:
        (PROFILE / ".legacy-imported").touch()


def persistent_root(source):
    path = Path(source or BASE)
    return None if path == BASE else str(path)


class QueueStream(TextIOBase):
    def __init__(self, report):
        self.report = report

    def write(self, value):
        if value.strip():
            self.report(value.strip())
        return len(value)


def catalog():
    official = catalog_update.active_catalog(PROFILE, BASE)
    directories = dict.fromkeys([directory for _, directory, _, _ in CATALOGS] + ["apps-custom"])
    for directory in directories:
        source = PROFILE if directory == "apps-custom" else official
        for platform, path in discover_shard_files(str(source / directory)):
            if platform not in LABELS:
                continue
            for app in load_apps_array(path):
                if not isinstance(app, dict) or not app.get("id"):
                    continue
                if directory != "apps-custom" and catalog_update.is_retired_repository(app.get("repo_path")):
                    continue
                page = resolve_open_page_url(app)
                chrome = None
                if app.get("分类") == "浏览器扩展":
                    try:
                        chrome = extension_id(app.get("chrome_store_url") or page)
                    except ValueError:
                        pass
                if not (chrome or page or is_app_downloadable(app)):
                    continue
                yield dict(platform=platform, group="custom" if directory == "apps-custom" else platform,
                           directory=directory, catalog_root=str(source), app=app, url=page, chrome=chrome,
                           category=app.get("分类") or shard_label_from_filename(Path(path).name),
                           subcategory=app.get("子分类") or "")
                if directory == "apps" and platform == "windows" and (chrome or app.get("chrome_source_repo")):
                    yield dict(platform=platform, group="chrome", directory=directory, app=app,
                               url=page, chrome=chrome, category=app.get("子分类") or "其他",
                               subcategory="")


class App:
    def __init__(self, window):
        self.window = window
        window.title("GH Release Fetch - github.com/shellsec/gh-release-fetch")
        window.geometry("1160x820")
        window.minsize(900, 675)
        self.events = Queue()
        self.active = None
        self.clear_pending = None
        self.stop = Event()
        self.closing = False
        self.resolver_busy = False
        self.web_catalog_running = False
        self.catalog_check_running = False
        self.checked = set()
        self.state_path = PROFILE / "catalog_downloads" / "queue.json"
        self.log_path = self.state_path.with_name("download.log")
        self.tasks = self.load_tasks()
        self.load_catalog()
        assets = Path(getattr(sys, "_MEIPASS", ROOT / "release" / "windows"))
        self.icons = {key: tk.PhotoImage(data=(assets / "gui-icons" / f"{key}.png").read_bytes(), format="png")
                      for key in ("all", "app", *LABELS)}
        self.icons.update({
            path.stem.removeprefix("category-"): tk.PhotoImage(data=path.read_bytes(), format="png")
            for path in (assets / "gui-icons").glob("category-*.png")
        })
        window.iconphoto(True, self.icons["app"])
        self.visible = {}
        self.results = {}
        self.output = tk.StringVar(value=str(Path.home() / "Downloads" / "GHReleaseFetch"))
        self.threads = tk.StringVar(value="4")
        self.route = tk.StringVar(value="自动测速")
        self.query = tk.StringVar()
        self.status = tk.StringVar()
        self.downloadable_only = tk.BooleanVar()
        self.checked_only = tk.BooleanVar()
        self.catalog_status = tk.StringVar()
        self.settings_path = self.state_path.with_name("settings.json")
        self.language = "zh-CN"
        self.reload_language = False
        self.load_settings()
        set_language(self.language)
        self.kinds = {tr(label): key for label, key in KINDS.items()}
        self.route.set(tr(self.route.get()))
        self.layout()
        self.render()
        for task in self.tasks:
            self.update_task(task)
        window.protocol("WM_DELETE_WINDOW", self.close)
        window.after(80, self.poll)
        window.after(250, lambda: self.check_catalog(automatic=True))

    def load_catalog(self):
        self.entries = {}
        for row in catalog():
            key = (row["group"], row["platform"], row["directory"], row["app"]["id"])
            self.entries.setdefault(key, row)

    def check_catalog(self, automatic=False):
        if self.closing or self.catalog_check_running or automatic and not catalog_update.check_due(PROFILE):
            return
        self.catalog_check_running = True
        self.catalog_status.set(tr("正在检查在线清单…"))

        def worker():
            try:
                changed = catalog_update.update(PROFILE, lambda value: self.events.put(("catalog-status", None, value)))
                catalog_update.mark_checked(PROFILE)
                self.events.put(("catalog-finished", None, changed))
            except Exception as exc:
                self.events.put(("catalog-finished", None, tr("清单检查失败 · {error}").format(error=exc)))

        Thread(target=worker, daemon=True).start()

    def load_tasks(self):
        if not self.state_path.exists():
            return []
        try:
            tasks = json.loads(self.state_path.read_text(encoding="utf-8"))
            if not isinstance(tasks, list) or any(
                not isinstance(row, dict) or not {"id", "title", "kind", "state", "source", "output", "threads"} <= row.keys()
                or row["state"] not in STATES for row in tasks
            ):
                raise ValueError(tr("任务记录格式错误"))
        except (OSError, ValueError) as exc:
            messagebox.showerror("无法读取下载队列", f"{self.state_path}\n{exc}")
            raise
        for task in tasks:
            if task["state"] in ("active", "waiting"):
                task["state"] = "paused"
        return tasks

    def save(self):
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        atomic_json(self.state_path, self.tasks)

    def save_settings(self):
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        route = "auto" if self.route.get() == tr("自动测速") else self.route.get()
        atomic_json(self.settings_path, dict(output=self.output.get(), threads=self.threads.get(), route=route,
                                            language=self.language))

    def write_log(self, task, message):
        timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
        try:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.log_path.open("a", encoding="utf-8") as stream:
                for line in message.splitlines():
                    stream.write(f"{timestamp} [{task['id']}] {task['title']} · {line}\n")
        except OSError as exc:
            self.log_error = str(exc)

    def load_settings(self):
        try:
            settings = json.loads(self.settings_path.read_text(encoding="utf-8"))
            self.output.set(settings["output"])
            self.threads.set(settings["threads"])
            self.route.set("自动测速" if settings["route"] == "auto" else settings["route"])
            if settings.get("language") in ("zh-CN", "en"):
                self.language = settings["language"]
        except (OSError, ValueError, KeyError, TypeError):
            pass

    def change_language(self, language):
        if language == self.language:
            return
        previous = self.language
        self.language = language
        try:
            self.save_settings()
        except OSError as exc:
            self.language = previous
            messagebox.showerror(tr("无法保存设置"), str(exc), parent=self.window)
            return
        if self.active or any(task["state"] == "waiting" for task in self.tasks) or self.resolver_busy or self.catalog_check_running or self.web_catalog_running or len(self.window.winfo_children()) > self.main_children:
            messagebox.showinfo(tr("语言"), tr("语言已保存，下次启动时生效。"), parent=self.window)
            return
        self.reload_language = True
        self.window.destroy()

    def layout(self):
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("Treeview", rowheight=27)
        style.configure("Treeview.Heading", padding=(6, 5))
        style.configure("Accent.TButton", font=("Microsoft YaHei UI", 10, "bold"))
        import tkinter.font as font

        for name in ("TkDefaultFont", "TkTextFont", "TkHeadingFont"):
            font.nametofont(name).configure(family="Microsoft YaHei UI", size=10)
        root = ttk.Frame(self.window, padding=12)
        root.pack(fill="both", expand=True)
        settings = ttk.Frame(root)
        settings.pack(fill="x", pady=(0, 9))
        ttk.Label(settings, text=tr("保存位置")).pack(side="left")
        ttk.Entry(settings, textvariable=self.output).pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(settings, text=tr("选择目录"), command=self.choose_output).pack(side="left")
        ttk.Button(settings, text=tr("打开网页目录"), command=self.open_web_catalog).pack(side="left", padx=(4, 0))
        ttk.Label(settings, text=tr("连接数")).pack(side="left", padx=(14, 4))
        ttk.Combobox(settings, textvariable=self.threads, values=("1", "2", "4", "8"), state="readonly", width=4).pack(side="left")
        tabs = ttk.Notebook(root)
        self.tabs = tabs
        tabs.pack(fill="both", expand=True)
        browse = ttk.Frame(tabs, padding=10)
        external = ttk.Frame(tabs, padding=12)
        tabs.add(browse, text=tr("平台目录"))
        tabs.add(external, text=tr("链接加速下载"))
        self.external_tab = external
        from tools.gui_library import Library

        self.library = Library(self, tabs, PROFILE, BASE, CUSTOM, {key: tr(label) for key, label in LABELS.items()})
        menu = tk.Menu(self.window)
        search_menu = tk.Menu(menu, tearoff=False)
        search_menu.add_command(label=tr("软件资讯搜索"), command=lambda: self.library.search_pages(False))
        search_menu.add_command(label=tr("游戏搜索"), command=lambda: self.library.search_pages(True))
        menu.add_cascade(label=tr("资讯与游戏"), menu=search_menu)
        language_menu = tk.Menu(menu, tearoff=False)
        language_menu.add_command(label="简体中文", command=lambda: self.change_language("zh-CN"))
        language_menu.add_command(label="English", command=lambda: self.change_language("en"))
        menu.add_cascade(label=tr("语言"), menu=language_menu)
        menu.add_command(label="GitHub", command=lambda: webbrowser.open(
            "https://github.com/shellsec/gh-release-fetch"
        ))
        self.window.configure(menu=menu)
        filters = ttk.Frame(browse)
        filters.pack(fill="x", pady=(0, 8))
        ttk.Label(filters, text=tr("搜索")).pack(side="left")
        query = ttk.Entry(filters, textvariable=self.query)
        query.pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(filters, text=tr("清除搜索"), command=lambda: self.query.set("")).pack(side="left")
        ttk.Button(filters, text=tr("在线更新清单"), command=self.check_catalog).pack(side="left", padx=(5, 0))
        ttk.Checkbutton(filters, text=tr("可下载"), variable=self.downloadable_only, command=self.render).pack(side="left", padx=5)
        ttk.Checkbutton(filters, text=tr("已勾选"), variable=self.checked_only, command=self.render).pack(side="left")
        ttk.Label(browse, textvariable=self.catalog_status).pack(anchor="w")
        split = ttk.Panedwindow(browse, orient="horizontal")
        split.pack(fill="both", expand=True)
        left = ttk.Frame(split, width=210)
        right = ttk.Frame(split)
        split.add(left, weight=0)
        split.add(right, weight=1)
        self.categories = self.tree(left, (), tr("平台与分类"))
        self.populate_categories()
        self.categories.bind("<<TreeviewSelect>>", lambda _: self.render())
        self.table = self.tree(right, (("platform", tr("平台"), 95), ("category", tr("分类"), 118),
                                       ("repo", tr("仓库 / ID"), 180), ("mode", tr("入口"), 100)), tr("软件"))
        self.table.column("#0", width=290, minwidth=170)
        self.table.bind("<Double-1>", self.toggle_clicked)
        self.table.bind("<space>", lambda _: self.toggle(self.table.selection()))
        self.table.bind("<Button-1>", self.checkbox_click)
        self.table.bind("<Button-3>", self.catalog_menu)
        actions = ttk.Frame(browse)
        actions.pack(fill="x", pady=(8, 0))
        ttk.Label(actions, textvariable=self.status).pack(side="left")
        for label, callback in ((tr("批量下载"), self.enqueue_checked), (tr("导入清单"), self.import_saved_list),
                                (tr("获取仓库"), self.open_repository),
                                (tr("打开官网 / 商店"), self.open_selected),
                                (tr("清空勾选"), self.clear_checks), (tr("勾选当前结果"), self.check_visible)):
            style_name = "Accent.TButton" if label == tr("批量下载") else "TButton"
            ttk.Button(actions, text=label, command=callback, style=style_name).pack(side="right", padx=(4, 0))
        self.query.trace_add("write", self.filter_changed)
        self.external_panel(external)
        queue_frame = ttk.LabelFrame(root, text=tr("下载队列"), padding=8)
        queue_frame.pack(fill="x", pady=(10, 0))
        self.queue_table = self.tree(queue_frame, (("state", tr("状态"), 88), ("message", tr("进度 / 详情"), 550)), tr("任务"), height=6)
        self.queue_table.column("#0", width=325)
        self.queue_table.bind("<<TreeviewSelect>>", self.show_queue_detail)
        self.queue_table.bind("<Button-3>", self.queue_menu)
        actions = ttk.Frame(root)
        actions.pack(fill="x", pady=(6, 0))
        self.detail = tk.StringVar()
        ttk.Label(actions, textvariable=self.detail, wraplength=585).pack(side="left", fill="x", expand=True)
        for label, callback in ((tr("下载日志"), self.open_log), (tr("打开目录"), self.open_folder),
                                (tr("清理下载目录"), self.clean_downloads), (tr("全部清空"), self.clear_queue),
                                (tr("移除任务"), self.remove_tasks),
                                (tr("重试失败"), self.retry_failed),
                                (tr("继续 / 重试"), self.resume_tasks), (tr("暂停"), self.pause_tasks)):
            ttk.Button(actions, text=label, command=callback).pack(side="right", padx=(4, 0))
        query.focus_set()
        self.main_children = len(self.window.winfo_children())

    def populate_categories(self):
        tree = self.categories
        selected = (tree.selection() or ("windows",))[0]
        group = selected.partition(":")[0]
        category = tree.item(selected, "text") if ":" in selected else ""
        opened = {key for key in LABELS if tree.exists(key) and tree.item(key, "open")}
        tree.delete(*tree.get_children())
        tree.insert("", "end", iid="all", text=tr("所有平台"), image=self.icons["all"])
        target = group
        for key, label in LABELS.items():
            tree.insert("", "end", iid=key, text=tr(label), image=self.icons[key], open=key in opened)
            categories = sorted({row["category"] for row in self.entries.values() if row["group"] == key})
            for index, name in enumerate(categories):
                iid = f"{key}:{index}"
                icon = self.icons[CATEGORY_ICONS.get(name, "tools")]
                tree.insert(key, "end", iid=iid, text=tr(name), image=icon)
                if key == group and name == category:
                    target = iid
        tree.selection_set(target)

    @staticmethod
    def tree(parent, columns, label, height=10):
        box = ttk.Frame(parent)
        box.pack(fill="both", expand=True)
        table = ttk.Treeview(box, columns=[c[0] for c in columns], height=height)
        table.heading("#0", text=label)
        table.column("#0", width=190)
        for key, title, width in columns:
            table.heading(key, text=title)
            table.column(key, width=width, stretch=key == "message")
        vertical = ttk.Scrollbar(box, command=table.yview)
        vertical.pack(side="right", fill="y")
        table.configure(yscrollcommand=vertical.set)
        table.pack(side="left", fill="both", expand=True)
        return table

    def external_panel(self, frame):
        ttk.Label(frame, text=tr("GitHub 仓库、Release、附件链接，或 Chrome 商店链接 / 扩展 ID")).pack(anchor="w")
        self.source = tk.Text(frame, height=3, wrap="word", undo=True)
        self.source.pack(fill="x", pady=(5, 12))
        self.kind = tk.StringVar(value=tr("按链接识别"))
        self.ref = tk.StringVar()
        self.target = tk.StringVar()
        line = ttk.Frame(frame)
        line.pack(fill="x")
        ttk.Combobox(line, textvariable=self.kind, values=list(self.kinds), state="readonly", width=17).pack(side="left")
        ttk.Label(line, text=tr("标签 / 分支 / 提交")).pack(side="left", padx=(10, 5))
        ttk.Entry(line, textvariable=self.ref).pack(side="left", fill="x", expand=True)
        ttk.Label(line, text=tr("下载线路")).pack(side="left", padx=(10, 5))
        ttk.Combobox(line, textvariable=self.route, values=[tr("自动测速"), *dict(ROUTES)], state="readonly", width=20).pack(side="left")
        location = ttk.Frame(frame)
        location.pack(fill="x", pady=10)
        ttk.Label(location, text=tr("仓库保存路径（可选）")).pack(side="left")
        ttk.Entry(location, textvariable=self.target).pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(location, text=tr("选路径"), command=self.choose_target).pack(side="left")
        switches = ttk.Frame(frame)
        switches.pack(fill="x")
        self.options = {}
        for name, label in (("extract", tr("源码 ZIP 解压到同名目录")), ("shallow", tr("浅克隆")),
                            ("submodules", tr("递归子模块")), ("lfs", tr("获取 Git LFS 文件"))):
            self.options[name] = tk.BooleanVar()
            ttk.Checkbutton(switches, variable=self.options[name], text=label).pack(side="left", padx=(0, 12))
        actions = ttk.Frame(frame)
        actions.pack(fill="x", pady=13)
        ttk.Button(actions, text=tr("获取并加入队列"), command=self.external_add).pack(side="left")
        ttk.Button(actions, text=tr("一键提取"), command=self.extract_sources).pack(side="left", padx=6)
        ttk.Button(actions, text=tr("打开 Chrome 商店"), command=self.external_open).pack(side="left", padx=6)
        self.external_status = tk.StringVar()
        ttk.Label(frame, textvariable=self.external_status, wraplength=820).pack(anchor="w")

    def filter_changed(self, *_):
        pending = getattr(self, "filter_timer", None)
        if pending:
            self.window.after_cancel(pending)
        self.filter_timer = self.window.after(160, self.apply_filter)

    def apply_filter(self):
        self.filter_timer = None
        self.render()

    def render(self):
        selected = self.categories.selection()
        group, _, _ = (selected[0] if selected else "all").partition(":")
        category = self.categories.item(selected[0], "text") if selected and ":" in selected[0] else None
        query = self.query.get().strip()
        self.table.delete(*self.table.get_children())
        self.visible.clear()
        rows = []
        for key, row in self.entries.items():
            if self.checked_only.get() and key not in self.checked:
                continue
            if self.downloadable_only.get() and not (row["chrome"] or row["group"] == "chrome" or is_app_downloadable(row["app"])):
                continue
            if group != "all" and row["group"] != group or group == "all" and row["group"] == "chrome":
                continue
            if category and row["category"] != category:
                continue
            score = match_score(query, row["app"]) if query else 0
            if query and score < 40:
                continue
            rows.append((score, key, row))
        for _, key, row in sorted(rows, key=lambda item: (-item[0], item[1][-1].casefold())):
            app = row["app"]
            mode = tr("原版 CRX") if row["chrome"] else tr("Chrome 源码") if row["group"] == "chrome" else tr("下载附件") if is_app_downloadable(app) else tr("官方页面")
            iid = self.table.insert("", "end", text=self.row_title(key, row),
                                    values=(tr(LABELS[row["platform"]]), tr(row["category"]),
                                            app.get("repo_path") or app["id"], mode))
            self.visible[iid] = key
        self.update_count()

    def row_title(self, key, row):
        app = row["app"]
        return ("☑  " if key in self.checked else "☐  ") + (app.get("简介") or app["id"])

    def update_count(self):
        self.status.set(tr("{total} 项 · 已勾选 {checked} 项").format(total=len(self.visible), checked=len(self.checked)))

    def checkbox_click(self, event):
        iid = self.table.identify_row(event.y)
        if iid and self.table.identify_column(event.x) == "#0" and event.x < 31:
            self.toggle((iid,))
            return "break"

    def toggle_clicked(self, event):
        iid = self.table.identify_row(event.y)
        if iid and event.x >= 31:
            self.toggle((iid,))
        return "break"

    def toggle(self, iids):
        for iid in iids:
            key = self.visible[iid]
            self.checked.symmetric_difference_update((key,))
            self.table.item(iid, text=self.row_title(key, self.entries[key]))
        if self.checked_only.get():
            self.render()
        else:
            self.update_count()
        return "break"

    def check_visible(self):
        self.checked.update(self.visible.values())
        self.refresh_checks()

    def clear_checks(self):
        self.checked.clear()
        self.refresh_checks()

    def refresh_checks(self):
        if self.checked_only.get():
            self.render()
            return
        for iid, key in self.visible.items():
            self.table.item(iid, text=self.row_title(key, self.entries[key]))
        self.update_count()

    def current_rows(self):
        return [self.entries[key] for key in sorted(self.checked)] or [
            self.entries[self.visible[iid]] for iid in self.table.selection()
        ]

    def open_selected(self):
        self.open_rows(self.current_rows())

    def open_rows(self, rows):
        for row in rows:
            page = store_url(row["chrome"]) if row["chrome"] else row["url"]
            if urlsplit(page).scheme in ("http", "https"):
                webbrowser.open(page)

    @staticmethod
    def popup(event, actions):
        menu = tk.Menu(event.widget, tearoff=False)
        for label, callback in actions:
            menu.add_command(label=label, command=callback)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
        return "break"

    def catalog_menu(self, event):
        iid = self.table.identify_row(event.y)
        if not iid:
            return
        self.table.selection_set(iid)
        row = self.entries[self.visible[iid]]
        actions = [(tr("立即打开官网 / 商店"), lambda: self.open_rows([row])),
                   (tr("批量下载"), self.enqueue_checked), (tr("获取仓库"), self.open_repository),
                   (tr("加入个人清单"), lambda: self.library.save_rows([row])),
                   (tr("保存到个人清单并下载"), lambda: self.library.save_rows([row], download=True))]
        if row["chrome"] or row["group"] == "chrome" or is_app_downloadable(row["app"]):
            actions.insert(0, (tr("立即下载"), lambda: self.enqueue_rows([row], priority=True)))
        return self.popup(event, actions)

    def queue_menu(self, event):
        iid = self.queue_table.identify_row(event.y)
        if not iid:
            return
        if iid not in self.queue_table.selection():
            self.queue_table.selection_set(iid)
        actions = [(tr("打开所在目录"), self.open_folder), (tr("复制保存路径"), self.copy_path),
                                  (tr("查看任务日志"), lambda: self.open_log(task_only=True)), (tr("继续 / 重试"), self.resume_tasks),
                                  (tr("暂停"), self.pause_tasks), (tr("移除任务"), self.remove_tasks),
                                  (tr("全部清空"), self.clear_queue)]
        task = next((task for task in self.tasks if task["id"] == iid), None)
        if task and task["state"] == "done" and task.get("result"):
            actions.insert(0, (tr("直接打开"), lambda: self.open_result(task)))
        return self.popup(event, actions)

    def open_result(self, task):
        path = Path(task["result"])
        try:
            if not path.exists():
                messagebox.showinfo(tr("直接打开"), tr("下载结果已不存在，可从下载历史重新下载。"), parent=self.window)
                return
            if os.name == "nt":
                os.startfile(path)
            elif not webbrowser.open(path.resolve().as_uri()):
                raise OSError(tr("系统没有可用的打开程序"))
        except OSError as exc:
            messagebox.showerror(tr("无法打开下载结果"), f"{path}\n{exc}", parent=self.window)

    def open_repository(self):
        selected = self.table.selection()
        if len(selected) != 1:
            messagebox.showinfo(tr("获取仓库"), tr("请单击选中一条软件记录。"))
            return
        row = self.entries[self.visible[selected[0]]]
        app = row["app"]
        source = app.get("chrome_source_repo") or app.get("repo_path")
        if not source:
            messagebox.showinfo(tr("获取仓库"), tr("该条目没有 GitHub 仓库。"))
            return
        self.source.delete("1.0", "end")
        self.source.insert("1.0", source)
        self.kind.set(tr("源码 ZIP") if row["group"] == "chrome" else tr("按链接识别"))
        self.ref.set("")
        self.target.set("")
        self.tabs.select(self.external_tab)

    def choose_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output.set(folder)
            try:
                self.save_settings()
            except OSError as exc:
                messagebox.showerror(tr("无法保存设置"), str(exc))

    def open_web_catalog(self):
        if self.web_catalog_running:
            messagebox.showinfo(tr("网页目录"), tr("网页目录已启动，可在浏览器切回目录标签页。"))
            return
        from tools.catalog_server import serve

        self.web_catalog_running = True
        def run_server():
            try:
                serve(ROOT, report=lambda _: None, submit=self.submit_web_batch)
            except (OSError, ValueError) as exc:
                self.events.put(("web-error", None, str(exc)))

        Thread(target=run_server, daemon=True).start()

    def submit_web_batch(self, tokens):
        response = Queue(maxsize=1)
        self.events.put(("web-batch", response, tokens))
        try:
            tasks = response.get(timeout=10)
        except Empty as exc:
            raise ValueError(tr("桌面队列暂时无响应")) from exc
        if isinstance(tasks, Exception):
            raise ValueError(str(tasks))

        def status():
            states = [task["state"] for task in tasks]
            pending = any(state in ("active", "waiting") for state in states)
            return {"code": None if pending else int(any(state != "done" for state in states)),
                    "lines": [f"{task['title']} · {STATES.get(task['state'], '已移除')} · {task.get('message', '')}"
                              for task in tasks]}
        return status

    def choose_target(self):
        kind = self.kinds[self.kind.get()]
        target = filedialog.askdirectory() if kind == "git" else filedialog.asksaveasfilename()
        if target:
            self.target.set(target)

    def make_task(self, title, kind, source, **kwargs):
        output = self.output.get().strip()
        if not output:
            raise ValueError(tr("请选择下载保存目录"))
        if kwargs.get("target"):
            kwargs["target"] = str(Path(kwargs["target"]).expanduser().resolve())
        return dict(id=uuid4().hex, title=title, kind=kind, source=source,
                    output=str(Path(output).expanduser().resolve()), threads=int(self.threads.get()),
                    state="waiting", message="", **kwargs)

    def enqueue_checked(self):
        rows = self.current_rows()
        pages = sum(not (row["chrome"] or row["group"] == "chrome" or is_app_downloadable(row["app"])) for row in rows)
        if pages and len(rows) > 1 and not messagebox.askyesno(
            tr("批量处理"), tr("下载 {count} 项，打开 {pages} 个官方页面。继续？").format(count=len(rows) - pages, pages=pages), parent=self.window
        ):
            return
        if self.enqueue_rows(rows):
            self.clear_checks()

    def import_saved_list(self):
        from tools.app_list import load_list

        paths = filedialog.askopenfilenames(initialdir=ROOT, filetypes=[(tr("个人更新清单"), "*.json")])
        if not paths:
            return
        index = {(row["platform"], row["directory"], row["app"]["id"]): row
                 for row in self.entries.values() if row["group"] != "chrome"}
        rows, missing = [], []
        try:
            for path in paths:
                data = load_list(path)
                for item in data["items"]:
                    platform = item.get("platform") or data.get("platform") or "windows"
                    directory = item.get("path", "").replace("\\", "/").split("/")[0]
                    row = index.get((platform, directory, item["id"]))
                    if row is None:
                        matches = [value for (p, _, aid), value in index.items()
                                   if p == platform and aid == item["id"]]
                        row = matches[0] if len(matches) == 1 else None
                    if row is None:
                        missing.append(f"{platform}/{item['id']}")
                    else:
                        rows.append(row)
        except (OSError, ValueError, TypeError, KeyError) as exc:
            messagebox.showerror(tr("无法读取个人清单"), str(exc))
            return
        if missing:
            messagebox.showwarning(tr("清单条目缺失"), "\n".join(missing))
        if rows and messagebox.askyesno(tr("批量下载"), tr("从个人清单导入并处理 {count} 项？").format(count=len(rows))):
            self.enqueue_rows(rows)

    def enqueue_rows(self, rows, *, priority=False):
        try:
            return bool(self.enqueue(self.tasks_for_rows(rows), priority=priority))
        except (OSError, ValueError) as exc:
            messagebox.showerror(tr("无法加入下载队列"), str(exc))
            return False

    def tasks_for_rows(self, rows):
        try:
            tasks = []
            for row in rows:
                app = row["app"]
                title = app.get("简介") or app["id"]
                if row["chrome"]:
                    task = self.make_task(title, "crx", row["chrome"], catalog=True)
                elif row["group"] == "chrome":
                    task = self.make_task(title, "source", app["chrome_source_repo"])
                elif is_app_downloadable(app):
                    task = self.make_task(title, "catalog", app["id"], platform=row["platform"],
                                          directory=row["directory"], catalog_root=persistent_root(row.get("catalog_root")))
                elif urlsplit(row["url"]).scheme in ("http", "https"):
                    task = self.make_task(title, "page", row["url"])
                else:
                    continue
                tasks.append(task)
            return tasks
        except KeyError as exc:
            raise ValueError(tr("目录条目缺少字段：{error}").format(error=exc)) from exc

    @staticmethod
    def task_key(task):
        return tuple(task.get(field) for field in ("kind", "source", "platform", "directory", "catalog", "output",
                                                    "target", "ref", "extract", "shallow", "submodules", "lfs"))

    def enqueue(self, tasks, *, priority=False):
        existing = {self.task_key(task): task for task in self.tasks if task["state"] != "done"}
        submitted = {}
        for task in tasks:
            key = self.task_key(task)
            if key in existing:
                task = existing[key]
                submitted[task["id"]] = task
                if not priority or task is self.active:
                    continue
                self.tasks.remove(task)
                task.update(state="waiting", message="")
            existing[key] = task
            submitted[task["id"]] = task
            if priority:
                self.tasks.insert(0, task)
            else:
                self.tasks.append(task)
            self.update_task(task)
            self.write_log(task, f"加入队列 · 保存位置 {task.get('target') or task['output']}")
        self.save()
        self.save_settings()
        return list(submitted.values())

    def external_open(self):
        try:
            items = [extension_id(value) for value in self.source.get("1.0", "end").split()]
            if not items or not all(items):
                raise ValueError(tr("请粘贴 Chrome 商店链接或扩展 ID"))
            for item in dict.fromkeys(items):
                webbrowser.open(store_url(item))
        except ValueError as exc:
            messagebox.showerror(tr("无法打开商店"), str(exc))

    def external_add(self):
        if self.resolver_busy:
            return
        try:
            values = self.source.get("1.0", "end").split()
            if not values:
                raise ValueError(tr("请粘贴下载地址"))
            route = self.route.get()
            route = "auto" if route == tr("自动测速") else route
            target = self.target.get().strip() or None
            if target and len(set(values)) > 1:
                raise ValueError(tr("批量下载请清空单个文件保存路径"))
            tasks, repositories, catalog_rows = [], [], []
            for value in dict.fromkeys(values):
                if value.startswith("catalog:"):
                    catalog_rows.append(self.library.catalog_token(value))
                    continue
                chrome = extension_id(value)
                if chrome:
                    tasks.append(self.make_task(chrome, "crx", chrome, target=target))
                    continue
                try:
                    parsed = parse_repository(value)
                except ValueError:
                    address = urlsplit(value)
                    if address.scheme not in ("http", "https") or not address.hostname or address.username:
                        raise
                    tasks.append(self.make_task(address.path.rsplit("/", 1)[-1] or value, "direct", value,
                                                route=route, target=target))
                    continue
                if parsed["asset"] and parsed["ref"] and not self.kinds[self.kind.get()] and not self.ref.get().strip():
                    tasks.append(self.make_task(parsed["asset"], "direct", value, route=route, target=target,
                                                release_asset=True))
                else:
                    repositories.append((value, parsed))
            if tasks:
                self.enqueue(tasks)
            if catalog_rows:
                self.enqueue_rows(catalog_rows)
            if not repositories:
                self.external_status.set(tr("已加入下载队列"))
                return
            releases, ready = [], []
            for source, parsed in repositories:
                kind = self.kinds[self.kind.get()] or parsed["kind"] or "release"
                task = self.make_task(parsed["repo"], kind, source, ref=self.ref.get().strip(),
                                      route=route, target=target,
                                      **{key: value.get() for key, value in self.options.items()})
                (releases if kind == "release" else ready).append(task)
            if ready:
                self.enqueue(ready)
            self.pending_releases = releases
            self.next_release()
        except (OSError, ValueError) as exc:
            messagebox.showerror(tr("无法加入下载队列"), str(exc))

    def extract_sources(self):
        links = extract_links(self.source.get("1.0", "end-1c"))
        if not links:
            self.external_status.set(tr("未找到可用链接"))
            return
        self.source.delete("1.0", "end")
        self.source.insert("1.0", "\n".join(links))
        self.external_status.set(tr("已提取 {count} 条链接，可检查后加入队列").format(count=len(links)))

    def next_release(self):
        if not self.pending_releases:
            self.resolver_busy = False
            return
        task = self.pending_releases.pop(0)
        self.resolver_busy = True
        self.external_status.set(tr("正在读取 {title} 的发布附件…").format(title=task["title"]))
        Thread(target=self.resolve_release, args=(task,), daemon=True).start()

    def resolve_release(self, task):
        try:
            assets = release_assets(task["source"], task["ref"])
            self.events.put(("assets", task, assets))
        except Exception as exc:
            self.events.put(("assets", task, str(exc)))

    def choose_assets(self, task, assets):
        if isinstance(assets, str) or not assets:
            if messagebox.askyesno(tr("没有可用发布附件"),
                                   f"{task['title']}\n{assets or tr('没有发布附件')}\n" + tr("改为下载源码 ZIP？"),
                                   parent=self.window):
                self.enqueue([dict(task, kind="source")])
            self.next_release()
            return
        if len(assets) == 1:
            self.enqueue_assets(task, assets)
            self.next_release()
            return
        dialog = tk.Toplevel(self.window)
        dialog.title(tr("选择发布附件 · {title}").format(title=task["title"]))
        dialog.geometry("650x450")
        dialog.transient(self.window)
        dialog.grab_set()
        ttk.Label(dialog, text=tr("按 Ctrl 或 Shift 选择多个附件")).pack(anchor="w", padx=12, pady=8)
        listing = tk.Listbox(dialog, selectmode="extended")
        listing.pack(fill="both", expand=True, padx=12)
        for name, _ in assets:
            listing.insert("end", name)

        def confirm():
            selected = [assets[i] for i in listing.curselection()]
            if selected:
                self.enqueue_assets(task, selected)
                close_dialog()

        def close_dialog():
            dialog.destroy()
            self.next_release()

        dialog.protocol("WM_DELETE_WINDOW", close_dialog)
        ttk.Button(dialog, text=tr("加入下载队列"), command=confirm).pack(pady=10)
        listing.bind("<Return>", lambda _: confirm())

    def enqueue_assets(self, task, assets):
        try:
            if task["target"] and len(assets) > 1:
                raise ValueError(tr("选择多个附件时请清空单个文件保存路径"))
            self.enqueue([dict(task, id=uuid4().hex, title=f"{task['title']} · {name}",
                               source=url, ref="") for name, url in assets])
            self.external_status.set(tr("已加入 {count} 个发布附件").format(count=len(assets)))
        except (OSError, ValueError) as exc:
            messagebox.showerror(tr("无法加入下载队列"), str(exc))

    def update_task(self, task):
        iid = task["id"]
        values = (tr(STATES[task["state"]]), tr(task.get("message", "")))
        if self.queue_table.exists(iid):
            self.queue_table.item(iid, values=values)
        else:
            self.queue_table.insert("", "end", iid=iid, text=task["title"], values=values)

    def selected_tasks(self):
        selected = set(self.queue_table.selection())
        return [task for task in self.tasks if task["id"] in selected]

    def show_queue_detail(self, _=None):
        selected = self.selected_tasks()
        task = selected[0] if selected else {}
        self.detail.set(task.get("result") or task.get("target") or task.get("output", ""))

    def copy_path(self):
        selected = self.selected_tasks()
        if selected:
            task = selected[0]
            self.window.clipboard_clear()
            self.window.clipboard_append(task.get("result") or task.get("target") or task["output"])

    def open_log(self, task_only=False, history_task=None):
        if getattr(self, "log_error", None):
            messagebox.showwarning(tr("日志写入失败"), self.log_error)
        selected = [history_task] if history_task else self.selected_tasks() if task_only else []
        marker = f"[{selected[0]['id']}]" if selected else ""

        def matches(line):
            return not marker or line.split(" ", 2)[1:2] == [marker]

        try:
            with self.log_path.open(encoding="utf-8") as stream:
                from collections import deque

                lines = deque((line for line in stream if matches(line)), maxlen=2000)
        except FileNotFoundError:
            lines = []
        except OSError as exc:
            messagebox.showerror(tr("无法读取日志"), str(exc))
            return
        dialog = tk.Toplevel(self.window)
        dialog.title(tr("任务日志") if selected else tr("下载日志"))
        dialog.geometry("940x520")
        ttk.Label(dialog, text=str(self.log_path), padding=8).pack(anchor="w")
        content = ttk.Frame(dialog, padding=(8, 0, 8, 8))
        content.pack(fill="both", expand=True)
        area = tk.Text(content, wrap="word")
        scrollbar = ttk.Scrollbar(content, command=area.yview)
        area.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        area.pack(side="left", fill="both", expand=True)
        area.insert("1.0", "".join(lines) or tr("暂无日志"))
        area.configure(state="disabled")
        area.see("end")

        def clear_log():
            try:
                if self.log_path.exists():
                    temporary = self.log_path.with_name(self.log_path.name + ".tmp")
                    try:
                        with self.log_path.open(encoding="utf-8") as source, temporary.open("w", encoding="utf-8") as output:
                            output.writelines(line for line in source if not matches(line))
                        temporary.replace(self.log_path)
                    finally:
                        temporary.unlink(missing_ok=True)
            except (OSError, UnicodeError) as exc:
                messagebox.showerror(tr("无法清空日志"), str(exc), parent=dialog)
                return
            area.configure(state="normal")
            area.delete("1.0", "end")
            area.insert("1.0", tr("暂无日志"))
            area.configure(state="disabled")
            clear_button.configure(state="disabled")

        clear_button = ttk.Button(dialog, text=tr("清空此任务日志") if selected else tr("清空全部下载日志"), command=clear_log)
        clear_button.pack(anchor="e", padx=8, pady=(0, 8))

    def pause_tasks(self):
        selected = self.selected_tasks() or self.tasks
        for task in selected:
            if task["state"] == "waiting":
                task.update(state="paused", message=tr("已暂停"))
                self.update_task(task)
            elif task is self.active:
                if task["kind"] == "git":
                    task["message"] = tr("Git 克隆正在执行，完成后将更新状态")
                else:
                    self.stop.set()
                    task["message"] = tr("正在保存分片…")
                self.update_task(task)
        self.save()

    def resume_tasks(self):
        self.resume_rows(self.selected_tasks() or self.tasks)

    def retry_failed(self):
        self.resume_rows(task for task in self.tasks if task["state"] == "failed")

    def resume_rows(self, rows):
        for task in rows:
            if task["state"] in ("paused", "failed"):
                task.update(state="waiting", message="")
                self.update_task(task)
        self.save()

    def remove_tasks(self):
        for task in self.selected_tasks():
            if task is not self.active:
                self.tasks.remove(task)
                if task["state"] != "done":
                    task["state"] = "removed"
                self.queue_table.delete(task["id"])
        self.save()

    def clear_queue(self):
        active = self.active
        if active and not messagebox.askyesno(
            tr("清空下载队列"),
            tr("Git 克隆结束后移除，其他下载会暂停并保留分片。确定清空？")
            if active["kind"] == "git" else tr("当前任务会暂停并保留分片。确定清空？"),
            parent=self.window,
        ):
            return
        for task in self.tasks[:]:
            if task is not active:
                self.tasks.remove(task)
                if task["state"] != "done":
                    task["state"] = "removed"
                self.queue_table.delete(task["id"])
        if active is not None:
            self.clear_pending = active["id"]
            if active["kind"] == "git":
                active["message"] = tr("Git 克隆结束后从队列移除")
            else:
                self.stop.set()
                active["message"] = tr("正在保存分片，随后清空队列…")
            self.update_task(active)
        self.save()
        self.show_queue_detail()

    def clean_downloads(self):
        root = Path(self.output.get()).expanduser().resolve()
        protected = {
            Path(task["reserved_target"]).resolve()
            for task in self.tasks if task["state"] != "done" and task.get("reserved_target")
        }
        files = {}
        for task in self.library.history:
            if not task.get("result"):
                continue
            path = Path(task.get("reserved_target") or task["result"])
            try:
                if path.resolve() != path or not path.is_relative_to(root) or path in protected:
                    continue
                if path.is_file():
                    files[path] = path.stat()
            except (OSError, RuntimeError):
                continue
        if not files:
            messagebox.showinfo(tr("清理下载目录"), tr("当前保存目录没有可清理的已下载文件。"), parent=self.window)
            return

        dialog = tk.Toplevel(self.window)
        dialog.title(tr("清理下载目录"))
        dialog.transient(self.window)
        dialog.grab_set()
        panel = ttk.Frame(dialog, padding=12)
        panel.pack(fill="both", expand=True)
        ttk.Label(panel, text=str(root), wraplength=700).pack(anchor="w")
        ttk.Label(panel, text=tr("选择要永久删除的已下载文件。下载历史和日志会保留。")).pack(anchor="w", pady=6)
        table = self.tree(panel, (("size", tr("大小"), 110),), tr("文件"), height=12)
        table.column("#0", width=570)
        rows = {
            table.insert("", "end", text=str(path.relative_to(root)),
                         values=(f"{stat.st_size / 1024:,.1f} KB",)): (path, stat)
            for path, stat in sorted(files.items())
        }

        def delete_files(selected, confirm):
            if not selected:
                return
            if confirm and not messagebox.askyesno(
                tr("确认清理"), tr("永久删除选中的 {count} 个文件？").format(count=len(selected)), default="no", parent=dialog,
            ):
                return
            if self.active or any(task["state"] == "waiting" for task in self.tasks):
                messagebox.showinfo(tr("清理下载目录"), tr("请先暂停或等待队列中的下载完成。"), parent=dialog)
                return
            failures = []
            deleted = 0
            for row in selected:
                path, original = rows[row]
                try:
                    current = path.stat()
                    if path.resolve() != path or not os.path.samestat(current, original):
                        raise OSError(tr("文件已变化，请重新打开清理窗口"))
                    if current.st_mtime_ns != original.st_mtime_ns or current.st_size != original.st_size:
                        raise OSError(tr("文件内容已变化，请重新打开清理窗口"))
                    path.unlink()
                    table.delete(row)
                    deleted += 1
                except (OSError, RuntimeError) as exc:
                    failures.append(f"{path.name}：{exc}")
            if failures:
                messagebox.showwarning(tr("清理结果"), tr("已删除 {deleted} 项，失败 {failed} 项。").format(deleted=deleted, failed=len(failures)) + "\n"
                                       + "\n".join(failures[:5]), parent=dialog)
            else:
                messagebox.showinfo(tr("清理结果"), tr("已删除 {count} 项。").format(count=deleted), parent=dialog)
            if not table.get_children():
                dialog.destroy()

        actions = ttk.Frame(panel)
        actions.pack(fill="x", pady=(8, 0))
        ttk.Button(actions, text=tr("全选"), command=lambda: table.selection_set(table.get_children())).pack(side="left")
        ttk.Button(actions, text=tr("删除所选"), command=lambda: delete_files(table.selection(), True)).pack(side="left", padx=6)
        ttk.Button(actions, text=tr("一键清空（永久删除）"),
                   command=lambda: delete_files(table.get_children(), False)).pack(side="left")
        ttk.Button(actions, text=tr("关闭"), command=dialog.destroy).pack(side="right")

    def open_folder(self):
        selected = self.selected_tasks()
        task = selected[0] if selected else {}
        result = task.get("result")
        folder = Path(result or task.get("output") or self.output.get())
        if result and not folder.is_dir():
            folder = folder.parent
        if not folder.is_dir():
            messagebox.showinfo(tr("打开目录"), tr("目录尚未创建"))
            return
        if os.name == "nt":
            os.startfile(folder)
        else:
            webbrowser.open(folder.resolve().as_uri())

    def worker(self, task):
        def report(value):
            self.events.put(("progress", task, value))

        def reserve(path):
            response = Queue(maxsize=1)
            self.events.put(("reserve-target", response, (task, path)))
            try:
                error = response.get(timeout=10)
            except Empty as exc:
                raise OSError(tr("保存路径登记超时")) from exc
            if error:
                raise error

        try:
            stream = QueueStream(report)
            with redirect_stdout(stream), redirect_stderr(stream):
                result = execute(task, PROFILE, report, self.stop.is_set,
                                 lambda url: self.events.put(("resolved", task, url)), reserve)
            self.events.put(("finished", task, ("done", str(result or ""))))
        except DownloadPaused as exc:
            self.events.put(("finished", task, ("paused", str(exc))))
        except Exception as exc:
            self.events.put(("finished", task, ("failed", str(exc))))

    def poll(self):
        while True:
            try:
                event, task, value = self.events.get_nowait()
            except Empty:
                break
            if event == "assets":
                if not self.closing:
                    self.choose_assets(task, value)
                continue
            if event in ("library", "library-error"):
                if not self.closing:
                    try:
                        if event == "library":
                            task(value)
                        else:
                            messagebox.showerror(tr("操作失败"), value)
                    except Exception as exc:
                        messagebox.showerror(tr("操作失败"), str(exc))
                continue
            if event == "web-error":
                self.web_catalog_running = False
                messagebox.showerror(tr("网页目录"), value)
                continue
            if event == "web-batch":
                try:
                    if self.closing:
                        raise ValueError(tr("桌面程序正在退出"))
                    rows = [self.library.catalog_token(token) for token in value]
                    submitted = self.enqueue(self.tasks_for_rows(rows))
                    if not submitted:
                        raise ValueError(tr("清单没有可处理的项目"))
                    task.put(submitted)
                except (OSError, ValueError) as exc:
                    task.put(exc)
                continue
            if event == "reserve-target":
                row, path = value
                row["reserved_target"] = path
                try:
                    self.save()
                except OSError as exc:
                    task.put(exc)
                else:
                    task.put(None)
                continue
            if event == "catalog-status":
                self.catalog_status.set(value)
                continue
            if event == "catalog-finished":
                self.catalog_check_running = False
                if value is True:
                    self.load_catalog()
                    self.checked.intersection_update(self.entries)
                    self.populate_categories()
                    self.render()
                self.catalog_status.set(tr("清单已更新 · 网页刷新后生效") if value is True else
                                        tr("清单已是最新") if value is False else value)
                continue
            if event == "resolved":
                task["resolved_commit" if task["kind"] == "git" else "resolved_url"] = value
                continue
            if event == "progress":
                task["message"] = value
                if not value.startswith("下载进度"):
                    self.write_log(task, value)
            else:
                state, message = value
                task.update(state=state, message=message or tr("已打开官方页面"))
                if state == "done" and message:
                    task["result"] = message
                    self.library.record(task)
                self.write_log(task, f"{STATES[state]} · {task['message']}")
                self.active = None
                if task["id"] == self.clear_pending:
                    self.clear_pending = None
                    self.tasks.remove(task)
                    task["state"] = "removed"
                    self.queue_table.delete(task["id"])
                    self.save()
                    continue
                self.save()
            self.update_task(task)
        self.show_queue_detail()
        if self.closing and self.active is None:
            self.window.destroy()
            return
        if not self.closing and self.active is None:
            self.active = next((task for task in self.tasks if task["state"] == "waiting"), None)
            if self.active:
                self.active.update(state="active", message=tr("正在解析下载地址…"))
                self.write_log(self.active, tr("开始任务"))
                self.update_task(self.active)
                self.save()
                self.stop.clear()
                Thread(target=self.worker, args=(self.active,), daemon=True).start()
        self.window.after(80, self.poll)

    def close(self):
        if self.closing:
            return
        self.closing = True
        self.pause_tasks_on_close()
        try:
            self.save()
            self.save_settings()
        except OSError as exc:
            messagebox.showerror(tr("无法保存队列"), str(exc))

    def pause_tasks_on_close(self):
        for task in self.tasks:
            if task["state"] == "waiting":
                task.update(state="paused", message=tr("已暂停"))
        if self.active and self.active["kind"] != "git":
            self.stop.set()


def main():
    try:
        window = tk.Tk()
    except tk.TclError:
        if not getattr(sys, "frozen", False) or os.name != "nt":
            raise
        # Some restricted Windows sessions prevent Tcl from sourcing scripts in
        # the extraction directory even though Python can read them.
        from shutil import copytree
        from tempfile import TemporaryDirectory

        PROFILE.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(prefix=".gui-runtime-", dir=PROFILE) as folder:
            for variable in ("TCL_LIBRARY", "TK_LIBRARY"):
                source = Path(os.environ[variable])
                target = Path(folder) / source.name
                copytree(source, target)
                os.environ[variable] = str(target)
            return run_window(tk.Tk())
    return run_window(window)


def run_window(window):
    mutex = None
    try:
        if os.name == "nt":
            import ctypes
            import hashlib

            key = hashlib.sha256(str(PROFILE.resolve()).casefold().encode()).hexdigest()
            kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel.CreateMutexW.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_wchar_p]
            kernel.CreateMutexW.restype = ctypes.c_void_p
            kernel.CloseHandle.argtypes = [ctypes.c_void_p]
            mutex = kernel.CreateMutexW(None, False, "Local\\GHReleaseFetch-" + key)
            if not mutex:
                raise ctypes.WinError(ctypes.get_last_error())
            if ctypes.get_last_error() == 183:
                messagebox.showinfo("GH Release Fetch", tr("这个目录中的程序已打开。"), parent=window)
                window.destroy()
                return 0
        initialize_profile()
        while True:
            app = App(window)
            window.mainloop()
            if not app.reload_language:
                break
            window = tk.Tk()
    except (OSError, ValueError) as exc:
        messagebox.showerror("GH Release Fetch", str(exc), parent=window)
        window.destroy()
        return 1
    finally:
        if mutex:
            kernel.CloseHandle(mutex)
    return 0


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode in ("--gui-updater", "--gui-lookup"):
        import io


        # The windowed bootloader clears standard streams. Web jobs supply pipes.
        if os.name == "nt":
            import ctypes
            kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel.GetStdHandle.restype = ctypes.c_void_p
            if not kernel.GetStdHandle(-11):
                kernel.AttachConsole(ctypes.c_uint(-1))
        for name, number in (("stdin", 0), ("stdout", 1), ("stderr", 2)):
            inherited = getattr(sys, name)
            if inherited is not None:
                inherited.reconfigure(encoding="utf-8")
                continue
            if getattr(sys, name) is None:
                try:
                    import ctypes
                    import msvcrt

                    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
                    kernel.GetStdHandle.restype = ctypes.c_void_p
                    handle = kernel.GetStdHandle(-10 - number)
                    if not handle or handle == ctypes.c_void_p(-1).value:
                        raise OSError("standard stream unavailable")
                    reading = number == 0
                    fd = msvcrt.open_osfhandle(handle, os.O_RDONLY if reading else os.O_WRONLY)
                    stream = open(fd, "r" if reading else "w", encoding="utf-8", buffering=1, closefd=False)
                except OSError:
                    stream = io.StringIO()
                setattr(sys, name, stream)
        sys.argv.pop(1)
        if mode == "--gui-updater":
            from auto_update import main as updater
            sys.exit(updater(resumable=True))
        from lookup_app import main as lookup
        sys.exit(lookup())
    sys.exit(main())
