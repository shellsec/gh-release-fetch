"""Personal lists, download history and legacy page search for the GUI."""
from functools import wraps
import json
from pathlib import Path
import re
from threading import Thread
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from tkinter.scrolledtext import ScrolledText
from urllib.parse import unquote
from uuid import uuid4

from tools import app_list, custom_catalog
from tools import page_index_update
from tools.download_engine import atomic_json
from tools.gui_tasks import extract_links
from tools.gui_language import tr
from tools.repository_download import finish_action, parse_repository


def guarded(method):
    @wraps(method)
    def call(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except Exception as exc:
            messagebox.showerror(tr("操作失败"), str(exc), parent=self.app.window)
    return call


class Library:
    def __init__(self, app, tabs, root, base, custom, labels):
        self.app, self.root, self.base, self.custom, self.labels = app, root, base, custom, labels
        self.history_file = self.root / "catalog_downloads" / "history.json"
        self.history = self.read_history()
        lists = ttk.Frame(tabs, padding=8)
        history = ttk.Frame(tabs, padding=8)
        tabs.add(lists, text=tr("我的清单"))
        tabs.add(history, text=tr("下载历史"))
        subtabs = ttk.Notebook(lists)
        subtabs.pack(fill="both", expand=True)
        personal = ttk.Frame(subtabs, padding=6)
        custom = ttk.Frame(subtabs, padding=6)
        subtabs.add(personal, text=tr("个人更新清单"))
        subtabs.add(custom, text=tr("自定义清单"))
        self.personal_table = self.panel(personal, [
            (tr("下载所选"), lambda: self.download_personal(False)),
            (tr("下载全部"), lambda: self.download_personal(True)),
            (tr("从旧日志导入"), self.import_log),
            (tr("导入旧清单"), self.import_personal),
            (tr("移除所选"), self.remove_personal),
            (tr("刷新"), self.refresh_personal),
        ])
        self.custom_table = self.panel(custom, [
            (tr("添加来源"), self.add_custom), (tr("一键识别导入"), self.recognize_custom), (tr("编辑"), self.edit_custom), (tr("删除"), self.remove_custom),
            (tr("下载所选"), self.download_custom), (tr("导入"), self.import_custom), (tr("导出"), self.export_custom),
            (tr("撤销"), self.undo_custom), (tr("偏好"), self.preferences),
        ])
        self.history_table = self.panel(history, [
            (tr("批量重新下载"), lambda: self.replay(False)),
            (tr("批量获取最新版"), lambda: self.replay(True)),
            (tr("打开目录"), lambda: self.history_action(1)),
            (tr("任务日志"), self.history_log),
            (tr("旧版仓库记录"), self.import_repositories),
        ], history=True)
        self.history_table.bind("<Button-3>", self.history_menu)
        self.refresh_personal()
        self.refresh_custom()
        self.refresh_history()
        known = {task["id"] for task in self.history}
        for task in self.app.tasks:
            if task["state"] == "done" and task.get("result") and task["id"] not in known:
                self.record(task)

    def panel(self, parent, actions, history=False):
        bar = ttk.Frame(parent)
        bar.pack(fill="x", pady=(0, 6))
        for label, command in actions:
            ttk.Button(bar, text=label, command=command).pack(side="left", padx=(0, 4))
        columns = (("platform", tr("平台 / 类型"), 116), ("detail", tr("保存路径") if history else tr("清单 / 分类"), 520))
        return self.app.tree(parent, columns, tr("名称"))

    def official_rows(self):
        return {(row["platform"], row["directory"], row["app"]["id"]): row
                for row in self.app.entries.values() if row["group"] != "chrome"}

    def match_row(self, platform, app_id, directory=""):
        rows = self.official_rows()
        if directory and (platform, directory, app_id) in rows:
            return rows[(platform, directory, app_id)]
        candidates = [row for (p, _, aid), row in rows.items() if (p, aid) == (platform, app_id)]
        if len(candidates) != 1:
            raise ValueError(tr("找不到唯一清单条目：{item}").format(item=f"{platform}/{app_id}"))
        return candidates[0]

    def catalog_token(self, token):
        platform, separator, item = token.removeprefix("catalog:").partition("/")
        if not separator:
            raise ValueError(tr("无效网页清单条目：{token}").format(token=token))
        return self.match_row(platform, unquote(item))

    def saved_hit(self, row):
        platform, directory, app = row["platform"], row["directory"], row["app"]
        return dict(platform=platform, id=app["id"], path=f"{platform}/{app['id']}",
                    apps_dir=str(self.root / directory), 分类=row["category"], 简介=app.get("简介", ""))

    @guarded
    def save_rows(self, rows, download=False):
        app_list.save_hits_by_platform(str(self.root), [self.saved_hit(row) for row in rows], str(self.root / "apps"))
        self.refresh_personal()
        if download:
            self.app.enqueue_rows(rows)

    @guarded
    def refresh_personal(self):
        self.personal_table.delete(*self.personal_table.get_children())
        self.personal = {}
        for path in sorted(self.root.glob("saved_apps_*.json")):
            data = app_list.load_list(str(path))
            for item in data.get("items", []):
                platform = item.get("platform") or data.get("platform") or "windows"
                iid = self.personal_table.insert("", "end", text=item.get("简介") or item["id"],
                                                 values=(self.labels.get(platform, platform), path.name))
                self.personal[iid] = (path, item, platform)

    @guarded
    def download_personal(self, all_items):
        selected = self.personal if all_items else self.personal_table.selection()
        rows, errors = [], []
        for iid in selected:
            _, item, platform = self.personal[iid]
            try:
                directory = item.get("path", "").replace("\\", "/").split("/")[0]
                rows.append(self.match_row(platform, item["id"], directory))
            except ValueError as exc:
                errors.append(str(exc))
        if rows:
            self.app.enqueue_rows(rows)
        if errors:
            messagebox.showwarning(tr("部分条目无法下载"), "\n".join(errors), parent=self.app.window)

    @guarded
    def remove_personal(self):
        selected = self.personal_table.selection()
        if selected and messagebox.askyesno(tr("移除个人清单条目"), tr("移除所选 {count} 项？").format(count=len(selected))):
            for iid in selected:
                path, item, _ = self.personal[iid]
                app_list.remove_item(str(path), item)
            self.refresh_personal()

    @guarded
    def import_personal(self):
        paths = filedialog.askopenfilenames(filetypes=[(tr("个人清单"), "*.json")])
        hits = []
        for path in paths:
            data = app_list.load_list(path)
            for item in data.get("items", []):
                platform = item.get("platform") or data.get("platform") or "windows"
                directory = item.get("path", "").replace("\\", "/").split("/")[0] or "apps"
                hits.append(dict(item, platform=platform, apps_dir=str(self.root / Path(directory).name)))
        if hits:
            app_list.save_hits_by_platform(str(self.root), hits, str(self.root / "apps"))
            self.refresh_personal()

    @guarded
    def import_log(self):
        path = filedialog.askopenfilename(initialdir=self.root, filetypes=[(tr("旧版下载日志"), "*.txt *.log")])
        if not path:
            return
        platforms, keys = {}, set()
        with open(path, encoding="utf-8", errors="replace") as stream:
            for line in stream:
                start = re.search(r"=== \[([^\]]+)\] 开始 === \[平台: ([^\]]+)\]", line)
                if start:
                    platforms[start[1]] = start[2]
                done = re.search(r"\[([^\]]+)\] 安装包已下载:", line)
                if done and done[1] in platforms:
                    keys.add((platforms[done[1]], done[1]))
        rows = []
        for platform, aid in sorted(keys):
            try:
                rows.append(self.match_row(platform, aid))
            except ValueError:
                continue
        self.pick(tr("选择要加入个人清单的旧记录"), rows,
                  lambda row: row["app"].get("简介") or row["app"]["id"], self.save_rows)

    @guarded
    def refresh_custom(self):
        self.custom_table.delete(*self.custom_table.get_children())
        self.custom_rows = {}
        for row in custom_catalog.list_entries(str(self.custom)):
            app = row["app"]
            iid = self.custom_table.insert("", "end", text=app.get("简介") or app["id"],
                                           values=(self.labels.get(row["platform"], row["platform"]), app.get("分类", "")))
            self.custom_rows[iid] = row

    def custom_changed(self):
        self.app.load_catalog()
        self.app.checked.intersection_update(self.app.entries)
        self.app.populate_categories()
        self.app.render()
        self.refresh_custom()

    @guarded
    def download_custom(self):
        self.app.enqueue_rows([self.match_row(self.custom_rows[i]["platform"], self.custom_rows[i]["id"], "apps-custom")
                               for i in self.custom_table.selection()])

    @guarded
    def remove_custom(self):
        for iid in self.custom_table.selection():
            row = self.custom_rows[iid]
            if messagebox.askyesno(tr("移除自定义条目"), row["app"].get("简介", row["id"])):
                custom_catalog.delete_entry(str(self.custom), row["platform"], row["id"])
        self.custom_changed()

    @guarded
    def edit_custom(self):
        selection = self.custom_table.selection()
        if not selection:
            return
        row = self.custom_rows[selection[0]]
        self.add_custom(row)

    @guarded
    def add_custom(self, existing=None):
        dialog = tk.Toplevel(self.app.window)
        dialog.title(tr("编辑自定义来源") if existing else tr("添加自定义来源"))
        dialog.geometry("650x325")
        initial = existing["app"] if existing else {}
        prefs = custom_catalog.load_preferences(str(self.custom))
        fields = {}
        form = ttk.Frame(dialog, padding=12)
        form.pack(fill="both", expand=True)
        for key, label, default in (
            ("source", tr("仓库、文件地址或关键词"), initial.get("custom_source") or initial.get("repo_path", "")),
            ("name", tr("名称"), initial.get("简介", "")),
            ("category", tr("分类"), initial.get("分类", "自定义")),
            ("platform", tr("平台（可用逗号分隔）"), existing["platform"] if existing else prefs.get("platform", "windows")),
        ):
            ttk.Label(form, text=label).pack(anchor="w")
            var = fields[key] = tk.StringVar(value=default if isinstance(default, str) else "windows")
            ttk.Entry(form, textvariable=var).pack(fill="x", pady=(2, 6))
        download = tk.BooleanVar()
        ttk.Checkbutton(form, text=tr("保存后立即下载"), variable=download).pack(anchor="w")
        status = tk.StringVar()
        ttk.Label(form, textvariable=status).pack(anchor="w")

        def commit(entries):
            remove = (existing["platform"], existing["id"]) if existing else None
            custom_catalog.save_entries(str(self.custom), entries, remove_target=remove)
            self.custom_changed()
            if download.get():
                self.app.enqueue_rows([self.match_row(platform, item["id"], "apps-custom") for platform, item in entries])
            dialog.destroy()

        def submit():
            try:
                source = custom_catalog.parse_source(fields["source"].get())
                name, category = fields["name"].get(), fields["category"].get()
                platforms = list(dict.fromkeys(p.strip() for p in fields["platform"].get().split(",")))
                if any(p not in app_list.PLATFORMS for p in platforms):
                    raise ValueError(tr("可选平台：") + ", ".join(app_list.PLATFORMS))
                if source["kind"] == "fixed":
                    commit([(p, custom_catalog.make_fixed_entry(source["url"], p, name, category)) for p in platforms])
                    return
                status.set(tr("正在查找 GitHub 来源…"))

                def inspect(chosen):
                    def display(payload):
                        repo, tag, assets = payload
                        preferred = custom_catalog.preferred_asset_indices(assets, prefs)
                        assets = [assets[i] for i in preferred] + [asset for i, asset in enumerate(assets) if i not in preferred]
                        self.pick(tr("选择发布附件"), assets, lambda asset: asset["name"],
                                  lambda selected: commit([(p, custom_catalog.make_github_entry(repo["full_name"], tag, a, p, name, category))
                                                           for p in platforms for a in selected]))
                    self.background(lambda: custom_catalog.inspect_github(chosen), display)
                if source["kind"] == "search":
                    from tools.lookup_github_suggest import search_repos
                    self.background(lambda: search_repos(source["query"], True)[:10],
                                    lambda repos: self.pick(tr("选择仓库"), repos, lambda repo: repo["full_name"],
                                                            lambda selected: inspect({"kind": "github", "repo": selected[0]["full_name"]}), single=True))
                else:
                    inspect(source)
            except Exception as exc:
                status.set(str(exc))

        ttk.Button(form, text=tr("预览并保存"), command=submit).pack(anchor="e")

    @guarded
    def recognize_custom(self):
        from tools.lookup_github_suggest import GitHubSuggestError

        dialog = tk.Toplevel(self.app.window)
        dialog.title(tr("一键识别导入"))
        dialog.geometry("760x440")
        panel = ttk.Frame(dialog, padding=12)
        panel.pack(fill="both", expand=True)
        ttk.Label(panel, text=tr("粘贴包含 GitHub 仓库、发布附件或文件直链的文字")).pack(anchor="w")
        area = ScrolledText(panel, wrap="word")
        area.pack(fill="both", expand=True, pady=8)
        fallback = tk.StringVar(value=custom_catalog.load_preferences(str(self.custom)).get("platform", "windows"))
        if fallback.get() not in app_list.PLATFORMS:
            fallback.set("windows")
        ttk.Label(panel, text=tr("无法识别平台时归入")).pack(anchor="w")
        ttk.Combobox(panel, textvariable=fallback, values=tuple(app_list.PLATFORMS), state="readonly").pack(anchor="w")
        status = tk.StringVar()
        ttk.Label(panel, textvariable=status).pack(anchor="w")

        def recognize():
            links = extract_links(area.get("1.0", "end"))
            if not links:
                status.set(tr("没有识别到链接"))
                return
            platform = fallback.get()
            existing = {(row["platform"], row["id"]) for row in custom_catalog.list_entries(str(self.custom))}
            button.configure(state="disabled")
            status.set(tr("正在识别 {count} 个来源…").format(count=len(links)))

            def work():
                entries, failures = {}, []
                for link in links:
                    try:
                        source = custom_catalog.parse_source(link)
                        if source["kind"] == "github":
                            repo, tag, assets = custom_catalog.inspect_github(source)
                            name = repo["full_name"]
                            rows = [(p, custom_catalog.make_github_entry(name, tag, asset, p, name, "自定义"))
                                    for asset in assets for p in (asset["platforms"] or (platform,))]
                        elif source["kind"] == "fixed":
                            assets = custom_catalog.detect_assets([{"name": source["asset"]}])
                            if not assets:
                                raise ValueError(tr("无法识别下载文件类型"))
                            asset = assets[0]
                            rows = [(p, custom_catalog.make_fixed_entry(source["url"], p, asset["name"], "自定义"))
                                    for p in (asset["platforms"] or (platform,))]
                        else:
                            raise ValueError(tr("不支持此来源，请使用仓库或下载附件地址"))
                        for p, app in rows:
                            key = (p, app["id"])
                            if key not in existing:
                                entries.setdefault(key, (p, app))
                    except (ValueError, OSError, GitHubSuggestError) as exc:
                        failures.append(f"{link}：{exc}")
                return list(entries.values()), failures

            def display(result):
                if not dialog.winfo_exists():
                    return
                rows, failures = result
                button.configure(state="normal")
                status.set(tr("可导入 {count} 项，识别失败 {failed} 个来源，已跳过重复项。").format(count=len(rows), failed=len(failures)))
                if failures:
                    messagebox.showwarning(tr("识别结果"), "\n".join(failures[:8]), parent=dialog)
                if not rows:
                    return

                def save(selected):
                    custom_catalog.save_entries(str(self.custom), selected)
                    self.custom_changed()
                    dialog.destroy()

                self.pick(tr("选择要导入的条目（可多选）"), rows,
                          lambda row: f"{self.labels.get(row[0], row[0])} · {row[1]['简介']} · {row[1]['custom_asset_name']}",
                          save)

            self.background(work, display)

        button = ttk.Button(panel, text=tr("识别并预览"), command=recognize)
        button.pack(anchor="e")
        area.focus_set()

    @guarded
    def import_custom(self):
        path = filedialog.askopenfilename(filetypes=[(tr("自定义清单"), "*.json")])
        if path:
            custom_catalog.import_entries(str(self.custom), json.loads(Path(path).read_text(encoding="utf-8-sig")))
            self.custom_changed()

    @guarded
    def export_custom(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", initialfile="custom-catalog-export.json")
        if path:
            atomic_json(path, custom_catalog.export_entries(str(self.custom)))

    @guarded
    def undo_custom(self):
        custom_catalog.undo_last_change(str(self.custom))
        self.custom_changed()

    @guarded
    def preferences(self):
        prefs = custom_catalog.load_preferences(str(self.custom))
        fields = (("platform", tr("默认平台")), ("architecture", tr("默认架构")), ("package_kind", tr("默认包格式")))
        for key, title in fields:
            value = simpledialog.askstring(tr("自定义清单偏好"), title, initialvalue=prefs.get(key, ""))
            if value is None:
                return
            prefs[key] = value.strip()
        custom_catalog.save_preferences(str(self.custom), prefs)

    def read_history(self):
        try:
            data = json.loads(self.history_file.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except FileNotFoundError:
            return []

    def record(self, task):
        if task["kind"] != "page":
            if any(item["id"] == task["id"] for item in self.history):
                return
            self.history.insert(0, dict(task))
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            atomic_json(self.history_file, self.history)
            self.refresh_history()

    def refresh_history(self):
        self.history_table.delete(*self.history_table.get_children())
        self.records = {}
        for task in self.history:
            iid = self.history_table.insert("", "end", text=task["title"],
                                             values=(self.labels.get(task.get("platform"), task["kind"]), task.get("result", "")))
            self.records[iid] = task

    def selected_history(self):
        return [self.records[iid] for iid in self.history_table.selection()]

    @guarded
    def replay(self, latest, task=None):
        selected = [task] if task is not None else self.selected_history()
        if not selected:
            return
        folder = filedialog.askdirectory(title=tr("选择本次批量下载目录"), initialdir=self.app.output.get())
        if not folder:
            return
        from datetime import datetime
        from tools.catalog_update import active_catalog

        output = str(Path(folder) / ("batch-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f")))
        tasks = []
        for old in selected:
            task = dict(old, id=uuid4().hex, state="waiting", message="", output=output, target=None)
            for field in ("result", "resolved_url", "reserved_target"):
                task.pop(field, None)
            kind = task["kind"]
            if not latest and old.get("resolved_url"):
                task.update(kind="direct", source=old["resolved_url"], target=str(Path(output) / (task.get("platform") or "repository") / Path(old.get("result") or "download").name))
                if kind in ("release", "release-latest"):
                    task["release_asset"] = True
                if old.get("extract"):
                    task["target"] = None
            elif not latest and kind in ("source", "git") and old.get("resolved_commit"):
                task["ref"] = old["resolved_commit"]
            elif not latest and kind == "catalog":
                messagebox.showwarning(tr("缺少原附件记录"), f"{old['title']} · " + tr("可用「批量获取最新版」。"))
                continue
            elif latest and kind == "catalog" and task.get("directory") != "apps-custom":
                active = active_catalog(self.root, self.base)
                task["catalog_root"] = None if active == self.base else str(active)
            elif latest and (kind in ("release", "release-latest") or old.get("release_asset")):
                task.update(kind="release-latest", ref="")
            elif latest and kind in ("source", "git"):
                task.update(source=parse_repository(task["source"])["repo"], ref="")
            tasks.append(task)
        if tasks:
            self.app.enqueue(tasks)

    @guarded
    def history_action(self, action, task=None):
        selected = [task] if task is not None else self.selected_history()
        if selected and selected[0].get("result"):
            result = Path(selected[0]["result"])
            if not result.exists():
                messagebox.showinfo(tr("文件已不存在"), tr("文件已不存在，可从下载历史重新下载。"), parent=self.app.window)
                return
            if action == 5:
                content = []
                finish_action(action, result, self.root / "repository_downloads", report=content.append)
                dialog = tk.Toplevel(self.app.window)
                dialog.title(tr("查看 README"))
                dialog.geometry("820x550")
                area = ScrolledText(dialog, wrap="word")
                area.pack(fill="both", expand=True)
                area.insert("1.0", "\n".join(content))
                area.configure(state="disabled")
                return
            finish_action(action, result, self.root / "repository_downloads", report=lambda message:
                          messagebox.showinfo(tr("下载历史"), message, parent=self.app.window))

    @guarded
    def update_worktree(self, task=None):
        from tools.repository_download import update_git

        selected = [task] if task is not None else self.selected_history()
        if len(selected) == 1 and selected[0]["kind"] == "git":
            task = selected[0]
            self.background(lambda: update_git(task["result"], parse_repository(task["source"])["repo"]),
                            lambda _: messagebox.showinfo(tr("Git 更新"), tr("已更新工作区")))

    def history_log(self):
        selected = self.selected_history()
        if selected:
            self.app.open_log(history_task=selected[0])

    def history_menu(self, event):
        iid = self.history_table.identify_row(event.y)
        if not iid:
            return
        if iid not in self.history_table.selection():
            self.history_table.selection_set(iid)
        task = self.records[iid]
        result = Path(task["result"]) if task.get("result") else None
        actions = []
        if result and result.exists():
            actions.append((tr("打开所在目录"), lambda: self.history_action(1, task)))
            if result.is_dir() and (task.get("extract") or task.get("kind") == "git"):
                actions.extend([(tr("打开终端"), lambda: self.history_action(3, task)),
                                (tr("用编辑器打开"), lambda: self.history_action(4, task)),
                                (tr("查看 README"), lambda: self.history_action(5, task))])
                if task.get("kind") == "git":
                    actions.append((tr("更新 Git 工作区"), lambda: self.update_worktree(task)))
        else:
            latest = task.get("kind") == "catalog" and not task.get("resolved_url")
            label = tr("文件已不存在 · 获取最新版") if latest else tr("文件已不存在 · 重新下载")
            actions.append((label, lambda: self.replay(latest, task)))
        actions.append((tr("查看日志"), lambda: self.app.open_log(history_task=task)))
        return self.app.popup(event, actions)

    @guarded
    def import_repositories(self):
        path = self.root / "repository_downloads" / "repository_tasks.json"
        try:
            entries = json.loads(path.read_text(encoding="utf-8-sig"))
        except FileNotFoundError:
            messagebox.showinfo(tr("旧版仓库记录"), tr("没有找到旧版仓库记录。新版记录直接显示在下载历史中。"),
                                parent=self.app.window)
            return
        if not isinstance(entries, list):
            raise ValueError(tr("仓库历史格式错误"))
        known = {item.get("result") for item in self.history}
        imported = 0
        for item in entries:
            if item.get("status") != "completed" or item.get("result") in known:
                continue
            kind, source = item["kind"], item["repo"]
            if kind == "release" and item.get("asset"):
                from urllib.parse import quote
                source = f"https://github.com/{source}/releases/download/{quote(item['ref'], safe='')}/{quote(item['asset'])}"
            task = self.app.make_task(item["repo"], kind, source, ref=item.get("commit") or item.get("ref", ""))
            self.record(dict(task, state="done", result=item["result"]))
            known.add(item["result"])
            imported += 1
        messagebox.showinfo(tr("旧版仓库记录"), tr("已导入 {count} 条记录。").format(count=imported) if imported else tr("没有可导入的新记录。"),
                            parent=self.app.window)

    def background(self, work, callback):
        def worker():
            try:
                result = work()
                self.app.events.put(("library", callback, result))
            except Exception as exc:
                self.app.events.put(("library-error", None, str(exc)))
        Thread(target=worker, daemon=True).start()

    def pick(self, title, rows, label, callback, single=False):
        if not rows:
            messagebox.showinfo(title, tr("没有匹配项"))
            return
        dialog = tk.Toplevel(self.app.window)
        dialog.title(title)
        dialog.geometry("710x440")
        listing = tk.Listbox(dialog, selectmode="browse" if single else "extended")
        listing.pack(fill="both", expand=True, padx=8, pady=8)
        for row in rows:
            listing.insert("end", label(row))

        def confirm():
            items = [rows[i] for i in listing.curselection()]
            if not items:
                return
            try:
                callback(items)
            except Exception as exc:
                messagebox.showerror(tr("操作失败"), str(exc), parent=dialog)
                return
            dialog.destroy()

        ttk.Button(dialog, text=tr("确认"), command=confirm).pack(pady=(0, 8))
        listing.bind("<Return>", lambda _: confirm())

    def search_pages(self, games):
        from tools.soft_page_check import search_pages as pages

        dialog = tk.Toplevel(self.app.window)
        dialog.title(tr("游戏搜索") if games else tr("软件资讯搜索"))
        dialog.geometry("900x580")
        bar = ttk.Frame(dialog, padding=8)
        bar.pack(fill="x")
        query, scope, status = tk.StringVar(), tk.StringVar(value="gamer520" if games else ""), tk.StringVar()
        ttk.Entry(bar, textvariable=query).pack(side="left", fill="x", expand=True)
        if not games:
            ttk.Label(bar, text=tr("来源筛选")).pack(side="left", padx=6)
            ttk.Entry(bar, textvariable=scope, width=15).pack(side="left")
        table = self.app.tree(dialog, (("scope", tr("来源"), 100), ("url", tr("页面地址"), 360)), tr("标题"))
        table.column("#0", width=350)
        ttk.Label(dialog, textvariable=status).pack(anchor="w", padx=8, pady=5)
        rows = {}

        def render(results):
            if not dialog.winfo_exists():
                return
            table.delete(*table.get_children())
            rows.clear()
            for row in results:
                iid = table.insert("", "end", text=row.get("title") or row["url"], values=(row.get("scope", ""), row["url"]))
                rows[iid] = row
            status.set(tr("{count} 项").format(count=len(rows)))

        def submit():
            queries = query.get().split()
            scope_filter = scope.get()
            if not queries:
                return
            status.set(tr("搜索中…"))
            scopes = frozenset({"gamer520"}) if games else None
            def work():
                index = page_index_update.read(self.root, games)
                hits = pages.search(index if index is not None else pages.build_index(scopes), queries, scope_filter)
                return hits[:100] or pages._gamer520_live_fallback(queries, scope_filter, scopes, 40)
            self.background(work, render)

        def open_results():
            pages.open_urls([rows[i] for i in table.selection()])

        ttk.Button(bar, text=tr("搜索"), command=submit).pack(side="left", padx=5)
        ttk.Button(bar, text=tr("打开所选"), command=open_results).pack(side="left")
        dialog.bind("<Return>", lambda _: submit())
        table.bind("<Double-1>", lambda _: open_results())
