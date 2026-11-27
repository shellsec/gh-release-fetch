"""Windows disk cleanup menu and preview."""

import os
import stat
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from queue import Empty, Queue
from threading import Thread
from tkinter import messagebox, ttk

from tools import disk_cleanup
from tools.gui_language import tr

HIBERNATION_COMMANDS = (
    "& {\n"
    "    powercfg.exe /hibernate off\n"
    '    if ($LASTEXITCODE -ne 0) { throw "powercfg failed ($LASTEXITCODE)" }\n'
    '    if (Test-Path -LiteralPath "$env:SystemDrive\\hiberfil.sys" -ErrorAction Stop) {\n'
    '        cmd.exe /d /c \'del /f /q /a "%SystemDrive%\\hiberfil.sys"\'\n'
    "    }\n"
    '    Get-Item -Force -LiteralPath "$env:SystemDrive\\hiberfil.sys"\n'
    "}"
)
HIBERNATION_TERMINAL_HELP = (
    "在开始菜单搜索 Windows PowerShell，右键选择「以管理员身份运行」，"
    "并在用户账户控制提示中选择「是」。确认窗口标题为「管理员：Windows PowerShell」，"
    "在 PS 提示符后粘贴整段命令，按回车执行。"
)
HIBERNATION_RESULT_HELP = (
    "命令会先关闭休眠和快速启动，成功后才删除残留的休眠文件。"
    "最后提示找不到路径，表示休眠文件已移除。"
    "如果仍显示文件，请运行 powercfg.exe /a 查看休眠状态。"
)


class DiskCleanup:
    def __init__(self, app, tools, profile):
        self.app = app
        self.window = app.window
        self.profile = profile
        self.report = profile / "disk_cleanup" / "cleanup.log"
        self.busy = False
        actions = tk.Menu(tools, tearoff=False)
        actions.add_command(label=tr("磁盘清理预览…"), command=self.preview)
        actions.add_separator()
        actions.add_command(label=tr("一键清理 C 盘"), command=self.quick)
        actions.add_command(label=tr("查看磁盘清理日志"), command=self.open_log)
        tools.add_cascade(label=tr("磁盘清理"), menu=actions)

    def task_paths(self):
        task = self.app.active or {}
        roots = [Path(task["output"])] if task.get("output") else []
        if task.get("target"):
            roots.append(Path(task["target"]).parent)
        return tuple(path for path in roots if path.is_absolute())

    def scan(self, *, quick=False, protected=()):
        return disk_cleanup.scan(
            self.profile, self.app.log_path, quick=quick,
            active_log=self.app.active is not None,
            protected=protected, temp_protected=tuple(
                Path(path) for path in (getattr(sys, "_MEIPASS", ""), self.profile) if path),
        )

    def job(self, work, done):
        queue = Queue()
        self.busy = True

        def worker():
            try:
                queue.put((work(), None))
            except Exception as exc:
                queue.put((None, exc))

        def poll():
            try:
                value, error = queue.get_nowait()
            except Empty:
                self.window.after(100, poll)
                return
            self.busy = False
            if not self.app.closing:
                done(value, error)

        Thread(target=worker, daemon=True).start()
        self.window.after(100, poll)

    def open_log(self):
        try:
            os.startfile(str(self.report))
        except OSError as exc:
            messagebox.showinfo(tr("磁盘清理"), str(exc), parent=self.window)

    def result(self, value, error, parent):
        title = tr("磁盘清理")
        if error:
            messagebox.showerror(title, str(error), parent=parent)
            return
        removed, size, skipped, change = value
        summary = tr("已清理 {removed} 项，共 {size:,.2f} MiB。跳过 {skipped} 项。").format(
            removed=removed, size=size / 1048576, skipped=skipped)
        if change is not None:
            summary += "\n" + tr("C 盘净可用空间变化：{change:+,.2f} MiB").format(change=change / 1048576)
        if messagebox.askyesno(title, summary + "\n\n" + tr("查看磁盘清理日志？"), parent=parent):
            self.open_log()

    def quick(self):
        if self.busy:
            return
        active_log = self.app.active is not None
        protected = self.task_paths()
        self.job(
            lambda: disk_cleanup.clean(self.scan(quick=True, protected=protected), self.report,
                                       quick=True, active_log=active_log, protected=protected),
            lambda value, error: self.result(value, error, self.window),
        )

    def preview(self):
        if self.busy:
            return
        dialog = tk.Toplevel(self.window)
        dialog.title(tr("磁盘清理预览…"))
        dialog.geometry("1050x460")
        dialog.transient(self.window)
        dialog.grab_set()
        status = tk.StringVar(value=tr("正在扫描已知位置…"))
        ttk.Label(dialog, textvariable=status, padding=8).pack(anchor="w")
        frame = ttk.Frame(dialog)
        frame.pack(fill="both", expand=True, padx=8)
        tree = ttk.Treeview(frame, columns=("check", "name", "size", "path", "impact"), show="headings")
        for key, label, width in [
            ("check", "勾选", 54), ("name", "项目", 170), ("size", "大小 (MiB)", 95),
            ("path", "路径", 360), ("impact", "清理影响", 300),
        ]:
            tree.heading(key, text=tr(label))
            tree.column(key, width=width, stretch=key == "path")
        scrollbar = ttk.Scrollbar(frame, command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(fill="both", expand=True)
        rows = {}
        checked = set()

        def toggle(ids):
            for ident in ids:
                cache = rows.get(ident)
                if not cache or (not cache.files and cache.kind != "restore"):
                    continue
                checked.symmetric_difference_update((ident,))
                tree.set(ident, "check", "☑" if ident in checked else "☐")
            button.state(["!disabled"] if checked and not self.busy else ["disabled"])
            return "break"

        tree.bind("<Double-1>", lambda event: toggle((tree.identify_row(event.y),)))
        tree.bind("<space>", lambda event: toggle(tree.selection()))

        def selected_cache():
            selection = tree.selection()
            cache = rows.get(selection[0]) if selection else None
            return cache if cache and cache.kind not in ("restore", "notice") else None

        def locate():
            cache = selected_cache()
            if cache is None:
                return
            try:
                if not cache.path.exists():
                    messagebox.showinfo(dialog.title(), tr("此文件或目录已不存在。"), parent=dialog)
                elif cache.path.is_dir():
                    os.startfile(str(cache.path))
                else:
                    explorer = Path(os.environ.get("SystemRoot") or r"C:\Windows") / "explorer.exe"
                    subprocess.Popen([str(explorer), "/select,", str(cache.path)])
            except OSError as exc:
                messagebox.showerror(dialog.title(), str(exc), parent=dialog)

        def copy_path():
            cache = selected_cache()
            if cache is not None:
                dialog.clipboard_clear()
                dialog.clipboard_append(str(cache.path))

        context = tk.Menu(dialog, tearoff=False)
        context.add_command(label=tr("定位文件或目录"), command=locate)
        context.add_command(label=tr("复制路径"), command=copy_path)

        def hibernation_info():
            cache = selected_cache()
            if cache is None or cache.kind != "hibernate":
                return
            path = cache.path
            try:
                info = path.lstat()
            except FileNotFoundError:
                status = tr("文件不存在。")
            except OSError as exc:
                status = tr("无法确认文件状态。") + f"\n{exc}"
            else:
                attributes = info.st_file_attributes
                names = [tr(label) for flag, label in (
                    (stat.FILE_ATTRIBUTE_HIDDEN, "隐藏"),
                    (stat.FILE_ATTRIBUTE_SYSTEM, "系统"),
                    (stat.FILE_ATTRIBUTE_READONLY, "只读"),
                    (stat.FILE_ATTRIBUTE_ARCHIVE, "存档"),
                    (stat.FILE_ATTRIBUTE_REPARSE_POINT, "重解析点"),
                ) if attributes & flag]
                status = tr("文件存在。") + "\n" + tr("大小 {size:,} 字节").format(size=info.st_size)
                status += "\n" + tr("属性 {attributes}").format(attributes=f"0x{attributes:08X} " + ", ".join(names))
            guidance = "\n\n".join((
                tr("右键选择「复制关闭休眠命令」。"),
                tr(HIBERNATION_TERMINAL_HELP), HIBERNATION_COMMANDS, tr(HIBERNATION_RESULT_HELP),
            ))
            messagebox.showinfo(tr("查看文件信息"), f"{path}\n\n{status}\n\n{guidance}", parent=dialog)

        def open_drive():
            cache = selected_cache()
            if cache is None or cache.kind != "hibernate":
                return
            try:
                os.startfile(cache.path.anchor)
            except OSError as exc:
                messagebox.showerror(dialog.title(), str(exc), parent=dialog)

        hibernation_menu = tk.Menu(dialog, tearoff=False)
        hibernation_menu.add_command(label=tr("查看文件信息"), command=hibernation_info)
        hibernation_menu.add_command(label=tr("打开所在盘"), command=open_drive)
        hibernation_menu.add_command(label=tr("复制完整路径"), command=copy_path)

        def copy_hibernation_command():
            dialog.clipboard_clear()
            dialog.clipboard_append(HIBERNATION_COMMANDS)
            messagebox.showinfo(
                tr("关闭休眠"),
                "\n\n".join((tr("完整命令已复制。"), tr(HIBERNATION_TERMINAL_HELP),
                              tr(HIBERNATION_RESULT_HELP))),
                parent=dialog,
            )

        hibernation_menu.add_command(label=tr("复制关闭休眠命令"), command=copy_hibernation_command)

        def show_context(event):
            ident = tree.identify_row(event.y)
            if not ident:
                return
            tree.selection_set(ident)
            tree.focus(ident)
            state = "normal" if selected_cache() is not None else "disabled"
            for index in (0, 1):
                context.entryconfigure(index, state=state)
            popup = hibernation_menu if rows[ident].kind == "hibernate" else context
            try:
                popup.tk_popup(event.x_root, event.y_root)
            finally:
                popup.grab_release()

        tree.bind("<Button-3>", show_context)

        def finish(value, error):
            if dialog.winfo_exists():
                self.result(value, error, dialog)
                dialog.destroy()

        def clean_checked():
            if self.busy or not checked:
                return
            targets = [cache for ident, cache in rows.items() if ident in checked]
            prompt = tr("确认永久清理勾选的项目？")
            if any(cache.kind in ("restore", "hibernate") for cache in targets):
                prompt += "\n\n" + tr("删除还原点会失去对应的恢复机会。关闭休眠也会关闭快速启动。所选系统操作需要管理员权限。")
            if not messagebox.askyesno(dialog.title(), prompt, default=messagebox.NO, parent=dialog):
                return
            button.state(["disabled"])
            status.set(tr("正在清理…"))
            active_log = self.app.active is not None
            protected = self.task_paths()
            self.job(lambda: disk_cleanup.clean(targets, self.report, active_log=active_log,
                                                protected=protected), finish)

        button = ttk.Button(dialog, text=tr("清理勾选项目"), command=clean_checked)
        button.pack(anchor="e", padx=8, pady=8)
        button.state(["disabled"])

        def scanned(value, error):
            if not dialog.winfo_exists():
                return
            if error:
                status.set(str(error))
                return
            impacts = {
                "logs": "失去下载任务日志",
                "dumps": "失去崩溃排查资料",
                "prefetch": "下次启动可能变慢，受系统权限限制",
                "restore": "失去对应的恢复机会，需要管理员权限",
                "hibernate": "关闭休眠和快速启动，需要管理员权限",
                "notice": "扫描受限，请检查系统权限",
            }
            for cache in sorted(value, key=lambda item: item.size, reverse=True):
                size = "—" if cache.kind in ("restore", "notice") else f"{cache.size / 1048576:,.2f}"
                impact = impacts.get(cache.kind, "缓存可重新生成")
                if cache.kind == "logs" and not cache.files:
                    impact = "任务正在使用日志或日志无法访问"
                ident = tree.insert("", "end", values=(
                    "☐", tr(cache.name), size, str(cache.path), tr(impact),
                ))
                rows[ident] = cache
            status.set(tr("扫描完成。双击项目或按空格勾选。") if rows else tr("没有可显示的清理项目。"))

        protected = self.task_paths()
        self.job(lambda: self.scan(protected=protected), scanned)
