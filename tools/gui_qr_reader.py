"""Decode QR images locally and present results before acting on them."""
from threading import Thread
import tkinter as tk
from tkinter import filedialog, ttk
from urllib.parse import urlsplit
import webbrowser

from PIL import Image, ImageGrab, ImageOps
import zxingcpp

from tools.gui_language import tr
from tools.gui_link_converter import original_url


def read_codes(image):
    if image.width * image.height > 32_000_000:
        raise ValueError(tr("图片过大，请裁剪后重试。"))
    image = ImageOps.exif_transpose(image).convert("RGBA")
    background = Image.new("RGBA", image.size, "white")
    image = Image.alpha_composite(background, image).convert("L")
    codes = zxingcpp.read_barcodes(image, formats=zxingcpp.BarcodeFormat.QRCode)
    return list(dict.fromkeys(code.text for code in codes if code.text))


def read_file(path):
    with Image.open(path) as image:
        return read_codes(image)


def web_link(value):
    if any(c.isspace() or ord(c) < 32 for c in value) or "\\" in value:
        return False
    try:
        url = urlsplit(value)
        return (url.scheme in {"http", "https"} and bool(url.hostname)
                and url.username is None and (url.port is None or 0 < url.port <= 65535))
    except ValueError:
        return False


class QRReader(ttk.LabelFrame):
    def __init__(self, parent, app, convert):
        super().__init__(parent, text=tr("识别二维码"), padding=8)
        self.app = app
        self.convert = convert
        self.values = []
        self.busy = False
        self.status = tk.StringVar(self)
        actions = ttk.Frame(self)
        actions.pack(fill="x")
        ttk.Button(actions, text=tr("粘贴截图"), command=self.paste).pack(side="left")
        ttk.Button(actions, text=tr("选择图片"), command=self.choose_file).pack(side="left", padx=(6, 0))
        ttk.Label(self, textvariable=self.status, wraplength=285).pack(anchor="w", pady=(6, 4))
        self.results = tk.Listbox(self, height=4, width=1, exportselection=False)
        self.results.pack(fill="x")
        self.results.bind("<<ListboxSelect>>", lambda _: self.show_selected())
        self.result = tk.Text(self, height=3, width=1, wrap="word", state="disabled")
        self.result.pack(fill="x", pady=(6, 4))
        buttons = ttk.Frame(self)
        buttons.pack(fill="x")
        self.copy_button = ttk.Button(buttons, text=tr("复制"), command=self.copy)
        self.open_button = ttk.Button(buttons, text=tr("打开"), command=self.open)
        self.convert_button = ttk.Button(buttons, text=tr("转加速链接"), command=self.use_github)
        for button in (self.copy_button, self.open_button, self.convert_button):
            button.pack(side="left", padx=(0, 5))
        self.show_selected()

    def paste(self):
        if self.busy:
            return
        try:
            image = ImageGrab.grabclipboard()
        except (OSError, ValueError) as exc:
            self.finish(exc)
            return
        if isinstance(image, Image.Image):
            self.start(lambda: read_codes(image))
        elif isinstance(image, list) and len(image) == 1:
            self.start(lambda: read_file(image[0]))
        else:
            self.finish([])
            self.status.set(tr("剪贴板没有图片，请先截图或选择本地图片。"))

    def choose_file(self):
        if self.busy:
            return
        path = filedialog.askopenfilename(parent=self, filetypes=[
            (tr("图片"), "*.png *.jpg *.jpeg *.bmp *.webp *.gif *.tif *.tiff"),
            (tr("所有文件"), "*.*"),
        ])
        if path:
            self.start(lambda: read_file(path))

    def start(self, decode):
        self.busy = True
        self.set_results([])
        self.status.set(tr("正在识别二维码…"))

        def work():
            try:
                value = decode()
            except Exception as exc:
                value = exc
            self.app.events.put(("library", self.finish, value))

        Thread(target=work, daemon=True).start()

    def finish(self, value):
        if not self.winfo_exists():
            return
        self.busy = False
        if isinstance(value, Exception):
            self.set_results([])
            self.status.set(tr("无法读取图片：{error}").format(error=value))
            return
        self.set_results(value)
        if not value:
            self.status.set(tr("没有识别到二维码。"))
        elif len(value) == 1:
            self.results.selection_set(0)
            self.show_selected()
            if self.github():
                self.use_github()
            else:
                self.status.set(tr("已识别二维码。"))
        else:
            self.status.set(tr("识别到 {count} 个结果，请选择一条。").format(count=len(value)))

    def set_results(self, values):
        self.values = values
        self.results.delete(0, "end")
        for value in values:
            self.results.insert("end", value.replace("\n", " "))
        self.show_selected()

    def selected(self):
        selected = self.results.curselection()
        return self.values[selected[0]] if selected else ""

    def github(self):
        try:
            return original_url(self.selected())
        except ValueError:
            return ""

    def show_selected(self):
        value = self.selected()
        self.result.configure(state="normal")
        self.result.delete("1.0", "end")
        self.result.insert("1.0", value)
        self.result.configure(state="disabled")
        for button, enabled in (
            (self.copy_button, bool(value)),
            (self.open_button, web_link(value)),
            (self.convert_button, bool(self.github())),
        ):
            button.configure(state="normal" if enabled else "disabled")

    def copy(self):
        if value := self.selected():
            self.clipboard_clear()
            self.clipboard_append(value)

    def open(self):
        value = self.selected()
        if web_link(value):
            webbrowser.open(value)

    def use_github(self):
        if url := self.github():
            self.convert(url)
            self.status.set(tr("已把 GitHub 链接送到左侧转换。"))
