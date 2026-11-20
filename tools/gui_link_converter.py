"""Manual GitHub link conversion and local QR generation."""
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from threading import Thread
import time
import tkinter as tk
from tkinter import ttk
from urllib.parse import urljoin, urlsplit
import webbrowser

import requests

from tools.download_engine import HEADERS, ROUTES
from tools.gui_language import tr


GITHUB_HOSTS = {
    "github.com", "raw.githubusercontent.com", "gist.github.com",
    "gist.githubusercontent.com", "codeload.github.com",
    "release-assets.githubusercontent.com", "objects.githubusercontent.com",
}


def original_url(value):
    url = value.strip()
    for _, prefix in ROUTES:
        if prefix and url.startswith(prefix):
            url = url[len(prefix):]
            break
    if not url or len(url) > 8192 or any(c.isspace() or ord(c) < 32 for c in url) or "\\" in url:
        raise ValueError(tr("请输入一条有效的 GitHub HTTPS 链接。"))
    try:
        address = urlsplit(url)
        valid = (address.scheme == "https" and address.hostname in GITHUB_HOSTS
                 and address.username is None and address.port in (None, 443))
    except ValueError:
        valid = False
    if not valid:
        raise ValueError(tr("请输入一条有效的 GitHub HTTPS 链接。"))
    return url


def direct_only(url):
    # Queries can carry access tokens or signed credentials.
    return bool(urlsplit(url).query) or urlsplit(url).hostname in {
        "release-assets.githubusercontent.com", "objects.githubusercontent.com",
    }


def test_route(target, url):
    """A link can be an HTML repository page or an actual downloadable file."""
    origin = urlsplit(url)
    is_page = origin.hostname in {"github.com", "gist.github.com"} and not any(
        segment in origin.path for segment in ("/releases/download/", "/archive/", "/raw/")
    )
    allowed = GITHUB_HOSTS | {urlsplit(target).hostname}
    start = time.monotonic()
    try:
        for _ in range(4):
            with requests.get(target, headers={**HEADERS, "Range": "bytes=0-65535"},
                              stream=True, timeout=(3, 3), allow_redirects=False) as response:
                if response.is_redirect:
                    target = urljoin(target, response.headers["Location"])
                    address = urlsplit(target)
                    if (address.scheme != "https" or address.hostname not in allowed
                            or address.username is not None or address.port not in (None, 443)):
                        return 0
                    continue
                if not 200 <= response.status_code < 300:
                    return 0
                html = "text/html" in response.headers.get("Content-Type", "").lower()
                deadline = time.monotonic() + 3
                sample = bytearray()
                for chunk in response.iter_content(4096):
                    sample.extend(chunk)
                    if len(sample) >= 65536 or time.monotonic() > deadline:
                        break
                if html:
                    if not is_page or not any(marker in sample for marker in (
                        b"github.githubassets.com", b'name="octolytics-', b'gist.github.com/assets/',
                    )):
                        return 0
                return len(sample) / max(time.monotonic() - start, 0.001)
    except (requests.RequestException, ValueError):
        pass
    return 0


def choose_route(url, probe=test_route):
    proxies = [(name, prefix + url) for name, prefix in ROUTES if prefix]
    with ThreadPoolExecutor(max_workers=4) as pool:
        speeds = list(pool.map(lambda item: probe(item[1], url), proxies))
    speed, route = max(zip(speeds, proxies), key=lambda item: item[0])
    return route if speed > 0 else ("direct", url)


class LinkConverter(ttk.LabelFrame):
    def __init__(self, parent, app):
        super().__init__(parent, text=tr("加速链接转换"), padding=8)
        self.app = app
        self.input = tk.StringVar(self)
        self.original = tk.StringVar(self)
        self.result = tk.StringVar(self)
        self.status = tk.StringVar(self)
        self.auto = tr("自动选线")
        self.direct = tr("GitHub 直连")
        self.route = tk.StringVar(self, self.auto)
        self.qr_source = tk.StringVar(self, tr("加速链接"))
        self.timer = None
        self.generation = 0
        self.running = False
        self.pending = None
        self.qr_visible = False

        ttk.Label(self, text=tr("原链接")).grid(row=0, column=0, sticky="w")
        ttk.Button(self, text=tr("粘贴"), command=self.paste).grid(row=0, column=1, sticky="e")
        self.input_box = ttk.Entry(self, textvariable=self.input, width=66)
        self.input_box.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(2, 4))
        self.link_actions(2, self.original)
        ttk.Label(self, text=tr("加速线路")).grid(row=3, column=0, sticky="w", pady=(7, 0))
        ttk.Combobox(self, textvariable=self.route, state="readonly", width=19,
                     values=(self.auto, self.direct, *(name for name, prefix in ROUTES if prefix))
                     ).grid(row=3, column=1, sticky="e", pady=(7, 0))
        ttk.Label(self, textvariable=self.status, wraplength=460).grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(3, 0))
        ttk.Label(self, text=tr("转换结果")).grid(row=5, column=0, sticky="w", pady=(5, 0))
        ttk.Entry(self, textvariable=self.result, state="readonly", width=66).grid(
            row=6, column=0, columnspan=2, sticky="ew", pady=(2, 4))
        self.link_actions(7, self.result)
        ttk.Button(self, text=tr("转二维码"), command=self.show_qr).grid(row=7, column=1, sticky="e")
        self.qr_frame = ttk.Frame(self)
        self.qr_frame.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        self.qr_frame.grid_remove()
        for label in (tr("加速链接"), tr("原链接")):
            ttk.Radiobutton(self.qr_frame, text=label, value=label, variable=self.qr_source,
                            command=self.render_qr).pack(side="left", anchor="n")
        self.qr_image = ttk.Label(self)
        self.qr_image.grid(row=9, column=0, columnspan=2, pady=(4, 0))
        self.qr_image.grid_remove()
        self.input.trace_add("write", self.changed)
        self.route.trace_add("write", self.changed)
        self.input_box.bind("<Return>", lambda _: self.convert_now())

    def link_actions(self, row, source):
        bar = ttk.Frame(self)
        bar.grid(row=row, column=0, sticky="w")
        ttk.Button(bar, text=tr("打开"), width=7, command=lambda: self.act(source, False)).pack(side="left")
        ttk.Button(bar, text=tr("复制"), width=7, command=lambda: self.act(source, True)).pack(side="left", padx=(4, 0))

    def paste(self):
        try:
            value = self.clipboard_get()
        except tk.TclError:
            self.status.set(tr("剪贴板没有文本。"))
            return
        self.input.set(value.strip())
        self.convert_now()

    def changed(self, *_):
        self.generation += 1
        self.pending = None
        self.result.set("")
        self.original.set("")
        self.status.set("")
        self.render_qr()
        if self.timer:
            self.after_cancel(self.timer)
        self.timer = self.after(300, self.convert_now)

    def convert_now(self):
        if self.timer:
            self.after_cancel(self.timer)
            self.timer = None
        if not self.input.get().strip():
            return
        try:
            url = original_url(self.input.get())
        except ValueError as exc:
            self.status.set(str(exc))
            return
        self.original.set(url)
        selected = self.route.get()
        if direct_only(url):
            self.complete("direct", url, tr("带参数或签名的链接使用直连。"))
        elif selected == self.auto:
            self.status.set(tr("正在测试加速线路…"))
            self.pending = (self.generation, url)
            self.start_probe()
        else:
            name = "direct" if selected == self.direct else selected
            self.complete(name, dict(ROUTES)[name] + url)
        self.render_qr()

    def start_probe(self):
        if self.running or self.pending is None:
            return
        generation, url = self.pending
        self.pending = None
        self.running = True

        def work():
            try:
                result = choose_route(url)
            except Exception:
                result = ("direct", url)
            self.app.events.put(("library", lambda value: self.probe_done(generation, value), result))

        Thread(target=work, daemon=True).start()

    def probe_done(self, generation, result):
        if not self.winfo_exists():
            return
        self.running = False
        if generation == self.generation:
            name, url = result
            self.complete(name, url, tr("暂无可用加速线路，已保留原链接。") if name == "direct" else "")
        self.start_probe()

    def complete(self, name, url, message=""):
        self.result.set(url)
        self.status.set(message or tr("当前线路：{route}").format(route=self.direct if name == "direct" else name))
        self.render_qr()

    def act(self, source, copy):
        url = source.get()
        if not url:
            return
        if copy:
            self.clipboard_clear()
            self.clipboard_append(url)
        else:
            webbrowser.open(url)

    def show_qr(self):
        self.qr_visible = not self.qr_visible
        if self.qr_visible:
            self.qr_frame.grid()
            self.qr_image.grid()
        else:
            self.qr_frame.grid_remove()
            self.qr_image.grid_remove()
        self.render_qr()

    def render_qr(self):
        if not self.qr_visible:
            return
        url = self.original.get() if self.qr_source.get() == tr("原链接") else self.result.get()
        self.qr_photo = None
        self.qr_image.configure(image="", text="")
        if not url:
            return
        from segno import DataOverflowError, make_qr

        try:
            qr = make_qr(url, error="m")
        except DataOverflowError:
            self.qr_image.configure(text=tr("链接太长，无法生成二维码。"))
            return
        buffer = BytesIO()
        qr.save(buffer, kind="png", scale=max(1, min(5, 148 // qr.symbol_size()[0])))
        self.qr_photo = tk.PhotoImage(master=self, data=buffer.getvalue(), format="png")
        self.qr_image.configure(image=self.qr_photo)
