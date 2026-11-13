"""Serve the offline catalog and run its existing downloader on loopback."""
from collections import deque
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import threading
import webbrowser


def serve(root, *, output=None, open_browser=True, command=None, report=print, submit=None):
    from tools.catalog_update import active_catalog, filter_catalog_page

    root = Path(root)
    token = secrets.token_urlsafe(32)
    marker = '<meta name="catalog-session" content="">'

    def read_page():
        page = (active_catalog(os.environ.get("GHRF_CATALOG_PROFILE", root),
                               os.environ.get("GHRF_CATALOG_BASE", root)) / "catalog.html").read_text(encoding="utf-8")
        if marker not in page:
            raise ValueError("目录页版本不支持网页下载，请重新生成 catalog.html")
        return filter_catalog_page(page).replace(marker, f'<meta name="catalog-session" content="{token}">', 1).encode()

    read_page()
    if command is None:
        command = [sys.executable]
        if Path(sys.executable).name.casefold() == "ghreleasefetch.exe":
            command.append("--gui-lookup")
        elif not getattr(sys, "frozen", False):
            command.append(str(root / "lookup_app.py"))
    hidden = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}
    lock = threading.Lock()
    jobs = {}

    def download(job, items):
        if submit is not None:
            try:
                status = submit(items)
                with lock:
                    job["status"] = status
            except (OSError, ValueError) as exc:
                with lock:
                    job["lines"].append(str(exc))
                    job["code"] = 1
            return
        args = [*command, "--repository", " ".join(items), "--no-prompt"]
        if output:
            args.extend(("--output", output))
        code = 1
        try:
            with subprocess.Popen(
                args, cwd=root, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
                env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"}, **hidden,
            ) as process:
                for line in process.stdout:
                    with lock:
                        job["lines"].append(line.rstrip()[:1200])
                code = process.wait()
        except OSError as exc:
            with lock:
                job["lines"].append(str(exc))
        finally:
            with lock:
                job["code"] = code

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def send(self, status, body, content_type):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.end_headers()
            self.wfile.write(body)

        def json(self, status, value):
            self.send(status, json.dumps(value, ensure_ascii=False).encode(), "application/json; charset=utf-8")

        def authorized(self):
            return (self.headers.get("Host") == host
                    and secrets.compare_digest(self.headers.get("X-Catalog-Session", "").encode(), token.encode()))

        def do_GET(self):
            if self.headers.get("Host") == host and self.path in ("/", "/catalog.html"):
                try:
                    page = read_page()
                except (OSError, ValueError):
                    self.json(HTTPStatus.SERVICE_UNAVAILABLE, {"error": "暂时无法读取网页目录"})
                    return
                self.send(HTTPStatus.OK, page, "text/html; charset=utf-8")
                return
            if not self.authorized():
                self.json(HTTPStatus.FORBIDDEN, {"error": "无效的目录会话"})
                return
            job_id = self.path.removeprefix("/api/download/")
            with lock:
                job = jobs.get(job_id)
                if job and "status" in job:
                    state = job["status"]()
                else:
                    state = {"code": job["code"], "lines": list(job["lines"])} if job else None
            if state is None:
                self.json(HTTPStatus.NOT_FOUND, {"error": "下载任务不存在"})
            else:
                self.json(HTTPStatus.OK, state)

        def do_POST(self):
            if (self.path != "/api/download" or not self.authorized()
                    or self.headers.get("Origin") != origin):
                self.json(HTTPStatus.FORBIDDEN, {"error": "无效的目录会话"})
                return
            try:
                length = int(self.headers.get("Content-Length", 0))
                if not 0 < length <= 12000 or self.headers.get_content_type() != "application/json":
                    raise ValueError
                items = json.loads(self.rfile.read(length))
                if not isinstance(items, list) or not items or any(
                    not isinstance(item, str) or not item.startswith("catalog:")
                    or not item.isascii() or any(char.isspace() for char in item)
                    for item in items
                ):
                    raise ValueError
            except (ValueError, UnicodeError):
                self.json(HTTPStatus.BAD_REQUEST, {"error": "下载清单无效或过长，请分批提交"})
                return
            with lock:
                busy = any((job["status"]()["code"] if "status" in job else job["code"]) is None
                           for job in jobs.values())
                if not busy:
                    if len(jobs) >= 8:
                        del jobs[next(iter(jobs))]
                    job_id = secrets.token_hex(12)
                    job = jobs[job_id] = {"code": None, "lines": deque(maxlen=100)}
            if busy:
                self.json(HTTPStatus.CONFLICT, {"error": "已有批量下载正在运行"})
                return
            threading.Thread(target=download, args=(job, items), daemon=True).start()
            self.json(HTTPStatus.ACCEPTED, {"job": job_id})

    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
        host = f"127.0.0.1:{server.server_port}"
        origin = f"http://{host}"
        report(f"目录已启动：{origin}/（保持此窗口开启）")
        if open_browser:
            webbrowser.open(origin + "/")
        server.serve_forever()
