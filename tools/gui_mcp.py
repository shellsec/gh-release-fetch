"""Desktop settings and tool dispatch for the local MCP service."""

from concurrent.futures import Future
from functools import lru_cache
import json
from ipaddress import IPv4Address
from pathlib import Path
import re
from secrets import token_urlsafe
import socket
import sys
import tkinter as tk
from time import monotonic
from tkinter import messagebox, ttk
from urllib.parse import quote, unquote, urlsplit

import requests

from lookup_app import match_score
from tools import program_update
from tools.app_download import resolve_open_page_url
from tools.download_engine import atomic_json
from tools.gui_language import tr
from tools.gui_link_converter import choose_route, original_url
from tools.gui_tasks import extract_links
from tools.local_mcp import PRIVATE, Server
from tools.mcp_client_config import CLIENTS, configure_client
from tools.mcp_pipe import LocalPipe
from tools.repository_download import api, parse_repository

PORT = 18765


def lan_addresses():
    addresses = []
    try:
        # A UDP connect selects a source interface without sending packets.
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.connect(("192.0.2.1", 9))
            addresses.append(probe.getsockname()[0])
    except OSError:
        pass
    try:
        addresses.extend(sorted({item[4][0] for item in
                                 socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET)}))
    except OSError:
        pass
    return [address for address in dict.fromkeys(addresses)
            if any(IPv4Address(address) in network for network in PRIVATE)]
PLATFORMS = ["windows", "darwin", "linux", "android", "android_tv", "switch", "ps4", "ps5",
             "vita", "xbox", "linux_handheld"]
ARCHITECTURES = {
    "x64": r"x86[-_]64|x64|amd64",
    "arm64": r"aarch64|arm64",
    "x86": r"x86(?![-_]64)|i[3-6]86|win32",
    "universal": r"universal2?",
}
PACKAGE_TYPES = ("tar.gz", "tar.xz", "appimage", "msix", "exe", "msi", "dmg", "pkg", "zip",
                 "7z", "deb", "rpm", "apk", "ipa", "nro")
PLATFORM_HINTS = {
    "windows": r"windows|win(?:32|64)?",
    "darwin": r"darwin|macos|osx|mac",
    "linux": r"linux",
    "android": r"android",
    "switch": r"switch",
}


def tool(name, description, required=(), **fields):
    properties = {key: {"type": kind} if isinstance(kind, str) else kind for key, kind in fields.items()}
    return dict(name=name, description=description,
                inputSchema=dict(type="object", properties=properties, required=list(required), additionalProperties=False))


TOOLS = {t["name"]: t for t in (
    tool("catalog_categories", "List public local catalog platforms and categories"),
    tool("catalog_search", "Search the public local catalog, including Agent Skills",
         query="string", platform="string", category="string"),
    tool("github_search", "Search GitHub repositories using official qualifiers such as language: and pushed:.",
         ("query",), query="string"),
    tool("release_assets", "List the latest or specified GitHub release attachments. Select an exact URL before downloading.",
         ("repository",), repository="string"),
    tool("convert_link", "Select an acceleration route for a GitHub URL.", ("url",), url="string"),
    tool("extract_links", "Extract and deduplicate download links.", ("text",), text="string"),
    tool("download", "Queue exact HTTPS URLs, or provide a repository plus platform, architecture and package_type. "
         "A repository queues an attachment only when exactly one match remains. Submit only after user approval.",
         urls={"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 30},
         repository="string", platform={"type": "string", "enum": PLATFORMS},
         architecture={"type": "string", "enum": list(ARCHITECTURES)},
         package_type={"type": "string", "enum": list(PACKAGE_TYPES)}),
    tool("download_status", "Check a task submitted through MCP.", ("task_id",), task_id="string"),
    tool("download_pause", "Pause an MCP download.", ("task_id",), task_id="string"),
    tool("download_resume", "Resume or retry an MCP download.", ("task_id",), task_id="string"),
    tool("catalog_status", "Check local catalog refresh status."),
    tool("catalog_refresh", "Start the existing public catalog refresh."),
)}

for name in ("catalog_categories", "catalog_search", "extract_links", "download_status", "catalog_status",
             "github_search", "release_assets", "convert_link"):
    TOOLS[name]["annotations"] = {
        "readOnlyHint": True,
        "openWorldHint": name in ("github_search", "release_assets", "convert_link"),
    }


def asset_details(asset):
    name = asset["name"].casefold()
    package = next((extension for extension in PACKAGE_TYPES if name.endswith("." + extension)), None)
    platforms = [platform for platform, pattern in PLATFORM_HINTS.items()
                 if re.search(rf"(?<![a-z0-9])(?:{pattern})(?![a-z0-9])", name)]
    implied = {"exe": "windows", "msi": "windows", "msix": "windows", "dmg": "darwin", "pkg": "darwin",
               "deb": "linux", "rpm": "linux", "appimage": "linux", "apk": "android", "nro": "switch"}
    platform = platforms[0] if len(platforms) == 1 else implied.get(package) if not platforms else None
    architectures = [arch for arch, pattern in ARCHITECTURES.items()
                     if re.search(rf"(?<![a-z0-9])(?:{pattern})(?![a-z0-9])", name)]
    return dict(name=asset["name"], url=asset["browser_download_url"], size=asset.get("size"),
                platform=platform, architecture=architectures[0] if len(architectures) == 1 else None,
                package_type=package)


def get_release_assets(repository):
    source = parse_repository(repository)
    if source["kind"] == "source":
        raise ValueError("Enter a repository or release URL.")
    tag = source["ref"]
    release = api(source["repo"] + "/releases/" + ("tags/" + quote(tag, safe="") if tag else "latest"))
    return dict(version=release["tag_name"], assets=[
        asset_details(asset) for asset in release["assets"]
        if not source["asset"] or asset["name"] == source["asset"]
    ])


@lru_cache(maxsize=32)
def search_github(query, cache_window):
    with requests.get("https://api.github.com/search/repositories",
                      params={"q": query, "per_page": 25}, timeout=(5, 12)) as response:
        if response.status_code in (403, 429) and (
            response.headers.get("X-RateLimit-Remaining") == "0" or response.status_code == 429
        ):
            return {"rate_limited": True, "retry_after_seconds": response.headers.get("Retry-After"),
                    "reset_at_unix": response.headers.get("X-RateLimit-Reset")}
        response.raise_for_status()
        result = response.json()
    return {"incomplete": result["incomplete_results"], "repositories": [
        {"repo": row["full_name"], "url": row["html_url"], "description": row["description"],
         "stars": row["stargazers_count"], "pushed_at": row["pushed_at"]} for row in result["items"]
    ]}


class DesktopMCP:
    def __init__(self, app, profile):
        self.app = app
        self.path = profile / "mcp.json"
        self.server = None
        self.pipe = None
        self.error = ""
        try:
            config = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(config, dict):
                config = {}
        except (OSError, ValueError):
            config = {}
        token = config.get("token")
        self.config = dict(enabled=config.get("enabled") is not False, lan=config.get("lan") is True,
                           downloads=config.get("downloads") is not False,
                           token=token if isinstance(token, str) and re.fullmatch(r"[\w-]{40,100}", token) else token_urlsafe(32))

    def stop(self):
        self.stop_http()
        if self.pipe:
            self.pipe.stop()
            self.pipe = None

    def stop_http(self):
        if self.server:
            self.server.stop()
            self.server = None

    def start(self):
        self.stop_http()
        self.error = ""
        if not self.config["enabled"]:
            return
        source_url = f"https://github.com/{program_update.REPOSITORY}"
        if program_update.VERSION != "0.0":
            source_url += f"/tree/{program_update.VERSION}"
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            atomic_json(self.path, self.config)
            if sys.platform == "win32" and not self.pipe:
                self.pipe = LocalPipe(self.path.parent, lambda: self.config, TOOLS, self.invoke, source_url)
        except OSError as exc:
            self.error = str(exc)
        try:
            self.server = Server("0.0.0.0" if self.config["lan"] else "127.0.0.1", PORT,
                                 self.config["token"], TOOLS, self.invoke, source_url=source_url)
            self.server.start()
        except OSError as exc:
            self.error = str(exc)

    def settings(self):
        dialog = tk.Toplevel(self.app.window)
        dialog.title(tr("本地 MCP"))
        panel = ttk.Frame(dialog, padding=16)
        panel.pack(fill="both", expand=True)
        labels = {"enabled": "随程序启动 MCP", "lan": "允许局域网访问", "downloads": "允许 MCP 提交与管理下载"}
        settings = {key: tk.BooleanVar(dialog, value=self.config[key]) for key in labels}
        for key, label in labels.items():
            ttk.Checkbutton(panel, text=tr(label), variable=settings[key]).pack(anchor="w")
        status = tk.StringVar(dialog)
        ttk.Label(panel, textvariable=status, wraplength=440).pack(anchor="w", pady=8)
        ttk.Label(panel, text=tr("局域网使用 HTTP，仅在可信网络开启，请勿映射到公网。"),
                  wraplength=440).pack(anchor="w")
        address = tk.StringVar(dialog, value="127.0.0.1")
        address_row = ttk.Frame(panel)
        address_row.pack(fill="x", pady=8)
        address_box = ttk.Combobox(address_row, textvariable=address, state="readonly")
        address_box.pack(side="left", fill="x", expand=True)

        def endpoint():
            return f"http://{address.get()}:{PORT}/mcp"

        def use_local_pipe():
            return address.get() == "127.0.0.1" and self.pipe is not None

        def show_status(_event=None):
            pending = any(value.get() != self.config[key] for key, value in settings.items())
            if pending:
                status.set(tr("待应用 · {address}").format(address=endpoint()) if settings["enabled"].get()
                           else tr("待应用 · MCP 将关闭"))
            else:
                status.set(self.error or (f"MCP · {endpoint()}" if self.server else tr("MCP 已关闭")))
            ready = "normal" if self.server and not pending else "disabled"
            apply_button.configure(state="normal" if pending else "disabled")
            can_connect = self.config["enabled"] and (self.pipe or self.server) and not pending
            instruction_button.configure(state="normal" if (use_local_pipe() or self.server) and self.config["enabled"]
                                         and not pending else "disabled")
            more_menu.entryconfigure(0, state=ready)
            more_menu.entryconfigure(2, state="disabled" if pending else "normal")
            more_menu.entryconfigure(3, state="normal" if can_connect else "disabled")

        def update_status(prefer_lan=False):
            network = lan_addresses() if settings["lan"].get() else []
            addresses = [*network, "127.0.0.1"]
            address_box.configure(values=addresses)
            if prefer_lan or address.get() not in addresses:
                address.set(addresses[0])
            show_status()

        address_box.bind("<<ComboboxSelected>>", show_status)

        def apply(rotate=False):
            previous = self.config.copy()
            self.config.update({key: value.get() for key, value in settings.items()})
            if rotate:
                self.config["token"] = token_urlsafe(32)
            try:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                atomic_json(self.path, self.config)
                self.start()
            except OSError as exc:
                self.error = str(exc)
                self.config = previous
            update_status()
            if rotate and not self.error:
                copy(tr("令牌已更新，完整 Codex 配置已复制。也可通过「连接 AI 客户端」写入新令牌。"))

        def copy(message=None):
            config = (
                f'[mcp_servers.gh_release_fetch]\nurl = "{endpoint()}"\n'
                f'http_headers = {{ Authorization = "Bearer {self.config["token"]}" }}\n'
            )
            self.app.window.clipboard_clear()
            self.app.window.clipboard_append(config)
            messagebox.showinfo(tr("复制 Codex 配置"), message or
                                tr("已复制完整配置，包含访问令牌。请粘贴到 Codex 的 config.toml。"), parent=dialog)

        def copy_token():
            self.app.window.clipboard_clear()
            self.app.window.clipboard_append(self.config["token"])

        def local_command():
            if getattr(sys, "frozen", False):
                return [sys.executable, "--mcp-stdio"]
            return [sys.executable, str(Path(__file__).resolve().parents[1] / "windows_gui.py"), "--mcp-stdio"]

        def copy_instruction():
            if use_local_pipe():
                command, *args = local_command()
                instruction = tr(
                    "请把 GH Release Fetch 添加为当前客户端的本机 MCP。使用 stdio，服务器名 gh_release_fetch。\n"
                    "可执行文件：{command}\n启动参数：{args}\n"
                    "保留其他 MCP 设置。配置后请调用 catalog_search 查询 Superpowers，确认连接可用。"
                ).format(command=command, args=json.dumps(args, ensure_ascii=False))
            else:
                instruction = tr(
                    "请把 GH Release Fetch 添加为当前客户端的 MCP。使用 Streamable HTTP，服务器名 gh_release_fetch。\n"
                    "连接地址：{url}\n请求头：Authorization: Bearer {token}\n"
                    "保留其他 MCP 设置，勿在回复中显示令牌。配置后请调用 catalog_search 查询 Superpowers，确认连接可用。"
                ).format(url=endpoint(), token=self.config["token"])
            self.app.window.clipboard_clear()
            self.app.window.clipboard_append(instruction)
            messagebox.showinfo(tr("复制安装指令"), tr("安装指令已复制。"), parent=dialog)

        def connect():
            choice = tk.Toplevel(dialog)
            choice.title(tr("连接 AI 客户端"))
            choice.transient(dialog)
            choice.grab_set()
            frame = ttk.Frame(choice, padding=16)
            frame.pack(fill="both", expand=True)
            client = tk.StringVar(choice, value="Codex")
            ttk.Combobox(frame, textvariable=client, values=CLIENTS, state="readonly").pack(fill="x")

            def register():
                try:
                    command = local_command() if self.pipe else None
                    configure_client(client.get(), endpoint(), self.config["token"], command=command)
                except Exception:
                    # Config parse errors can include sensitive snippets.
                    messagebox.showerror(tr("连接 AI 客户端"), tr("配置失败。请检查客户端配置格式和写入权限。"),
                                         parent=choice)
                    return
                choice.destroy()
                messagebox.showinfo(tr("连接 AI 客户端"),
                                    tr("已配置 {client}。请重新打开客户端以加载 MCP。").format(client=client.get()),
                                    parent=dialog)

            ttk.Button(frame, text=tr("一键配置"), command=register).pack(anchor="e", pady=(8, 0))

        actions = ttk.Frame(panel)
        actions.pack(fill="x", pady=(4, 0))
        apply_button = ttk.Button(address_row, text=tr("应用"), command=apply)
        apply_button.pack(side="left", padx=(8, 0))
        instruction_button = ttk.Button(actions, text=tr("复制安装指令"), command=copy_instruction)
        instruction_button.pack(side="left")
        more_button = ttk.Menubutton(actions, text=tr("更多"))
        more_menu = tk.Menu(more_button, tearoff=False)
        more_menu.add_command(label=tr("复制 Codex 配置"), command=copy)
        more_menu.add_command(label=tr("复制访问令牌"), command=copy_token)
        more_menu.add_command(label=tr("重新生成令牌"), command=lambda: apply(True))
        more_menu.add_command(label=tr("连接 AI 客户端"), command=connect)
        more_button.configure(menu=more_menu)
        more_button.pack(side="right")
        settings["lan"].trace_add("write", lambda *_: update_status(prefer_lan=True))
        for key in ("enabled", "downloads"):
            settings[key].trace_add("write", lambda *_: show_status())
        update_status(prefer_lan=True)

    def invoke(self, name, args):
        if name == "github_search":
            query = args["query"].strip()
            if not 0 < len(query) <= 256:
                raise ValueError("Enter a repository search query of up to 256 characters.")
            return search_github(query, int(monotonic() // 60))
        if name == "release_assets":
            return get_release_assets(args["repository"])
        if name == "convert_link":
            url = original_url(args["url"])
            route, converted = choose_route(url)
            return {"original": url, "route": route, "url": converted}
        if name == "extract_links":
            return extract_links(args["text"])[:100]
        if name == "download" and "repository" in args:
            if "urls" in args:
                raise ValueError("Provide either URLs or a repository.")
            criteria = {key: args.get(key) for key in ("platform", "architecture", "package_type")}
            release = get_release_assets(args["repository"])
            matches = [asset for asset in release["assets"] if all(
                not value or asset[key] == value for key, value in criteria.items()
            )]
            if len(matches) != 1 or not all(criteria.values()):
                return dict(state="select_attachment", version=release["version"], matching=matches,
                            assets=release["assets"] if not matches else matches)
            args = dict(urls=[matches[0]["url"]], platform=criteria["platform"])
        result = Future()
        self.app.events.put(("mcp", result, (name, args)))
        try:
            return result.result(timeout=12)
        finally:
            result.cancel()

    def on_gui(self, name, args):
        app = self.app
        if name in ("catalog_categories", "catalog_search"):
            rows = [row for row in app.entries.values() if row["group"] != "custom"]
            if name == "catalog_categories":
                return sorted({(row["platform"], row["category"], row["subcategory"] or "") for row in rows})
            query = args.get("query", "").strip()
            platform = args.get("platform")
            category = args.get("category")
            matches = {}
            for row in rows:
                if platform and platform != row["platform"] or category and category not in (row["category"], row["subcategory"]):
                    continue
                item = row["app"]
                score = match_score(query, item) if query else 40
                if score >= 40:
                    key = (row["platform"], item["id"])
                    matches.setdefault(key, (score, dict(id=item["id"], name=item.get("简介") or item["id"],
                        platform=row["platform"], category=row["category"], subcategory=row["subcategory"],
                        repo=item.get("repo_path"), url=resolve_open_page_url(item))))
            return [item for _, item in sorted(matches.values(), key=lambda match: -match[0])[:40]]
        if name in ("catalog_refresh", "catalog_status"):
            if name == "catalog_refresh":
                app.check_catalog()
            try:
                checked = float((self.path.parent / "catalog-updates" / "checked-at").read_text(encoding="ascii"))
            except (OSError, ValueError):
                checked = None
            return {"running": app.catalog_check_running, "status": app.catalog_status.get(), "checked_at_unix": checked}
        if name == "download":
            if not self.config["downloads"]:
                raise ValueError("MCP downloads are disabled.")
            urls = args["urls"]
            if not isinstance(urls, list) or not 1 <= len(urls) <= 30:
                raise ValueError("Provide between 1 and 30 exact HTTPS file URLs.")
            platform = args.get("platform")
            if platform is not None and platform not in TOOLS[name]["inputSchema"]["properties"]["platform"]["enum"]:
                raise ValueError("Unknown platform.")
            tasks = []
            for url in dict.fromkeys(urls):
                address = urlsplit(url)
                if address.scheme != "https" or not address.hostname or address.username is not None or address.fragment:
                    raise ValueError("Provide HTTPS file URLs without credentials or fragments.")
                resource = address.path.strip("/").split("/")[2:]
                if address.hostname == "github.com" and not (
                    len(resource) >= 4 and resource[:2] == ["releases", "download"]
                    or len(resource) == 4 and resource[:3] == ["releases", "latest", "download"]
                    or len(resource) >= 2 and resource[0] in ("archive", "raw")
                ):
                    raise ValueError("Preview the GitHub release and select an attachment URL first.")
                filename = unquote(address.path.rsplit("/", 1)[-1]) or "download"
                task = app.make_task(filename, "direct", url, route="auto", mcp=True)
                if platform:
                    task["output"] = str(Path(task["output"]) / platform)
                tasks.append(task)
            submitted = app.enqueue(tasks)
            return [{"id": t["id"], "state": t["state"]} if t.get("mcp") else {"state": "already_queued"} for t in submitted]
        task = next((t for t in app.tasks if t.get("mcp") and t["id"] == args["task_id"]), None)
        if task is None:
            raise ValueError("MCP task not found.")
        if name != "download_status" and not self.config["downloads"]:
            raise ValueError("MCP downloads are disabled.")
        if name == "download_pause":
            app.pause_rows([task])
        if name == "download_resume":
            app.resume_rows([task])
        total = task.get("total_bytes")
        downloaded = task.get("downloaded_bytes")
        return dict(id=task["id"], title=task["title"], state=task["state"], message=task["message"],
                    path=task.get("result") or task.get("reserved_target"),
                    route=task.get("transfer_route"), downloaded_bytes=downloaded, total_bytes=total or None,
                    speed_mib_s=task.get("speed_mib_s") if task["state"] == "active" else None,
                    percent=100 if task["state"] == "done" else
                    min(100, downloaded * 100 / total) if total and downloaded is not None else None,
                    error=task["message"] if task["state"] == "failed" else None)
