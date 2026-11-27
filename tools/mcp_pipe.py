"""Connect local MCP stdio clients to the running Windows desktop app."""

from hashlib import sha256
import json
from multiprocessing import AuthenticationError
from multiprocessing.connection import Client, Listener, deliver_challenge, answer_challenge
from threading import Event, Thread

from tools.local_mcp import dispatch

REQUEST_LIMIT = 131072
RESPONSE_LIMIT = 4194304


def pipe_address(profile):
    identity = sha256(str(profile.resolve()).casefold().encode()).hexdigest()
    return r"\\.\pipe\GHReleaseFetch-MCP-" + identity


def error_response(request, message, code=-32603):
    if isinstance(request, dict) and "id" not in request:
        return None
    return {"jsonrpc": "2.0", "id": request.get("id") if isinstance(request, dict) else None,
            "error": {"code": code, "message": message}}


class LocalPipe:
    def __init__(self, profile, settings, tools, invoke, source_url):
        self.address = pipe_address(profile)
        self.listener = Listener(self.address, family="AF_PIPE")
        self.settings = settings
        self.tools = tools
        self.invoke = invoke
        self.source_url = source_url
        self.closed = Event()
        self.thread = Thread(target=self.serve, daemon=True)
        self.thread.start()

    def serve(self):
        while not self.closed.is_set():
            try:
                connection = self.listener.accept()
            except (OSError, EOFError):
                break
            if self.closed.is_set():
                connection.close()
                break
            Thread(target=self.handle, args=(connection,), daemon=True).start()

    def handle(self, connection):
        with connection:
            try:
                config = self.settings()
                if not config["enabled"] or self.closed.is_set():
                    return
                token = config["token"].encode()
                deliver_challenge(connection, token)
                answer_challenge(connection, token)
                if not connection.poll(5):
                    return
                request = json.loads(connection.recv_bytes(REQUEST_LIMIT))
                config = self.settings()
                if config["enabled"] and config["token"].encode() == token and not self.closed.is_set():
                    response = dispatch(request, self.tools, self.invoke, self.source_url)
                else:
                    response = error_response(request, "The desktop MCP session has changed.")
                connection.send_bytes(json.dumps(response, ensure_ascii=False).encode())
            except (OSError, EOFError, ValueError, AuthenticationError):
                return

    def stop(self):
        self.closed.set()
        if self.thread.is_alive():
            try:
                with Client(self.address, family="AF_PIPE"):
                    pass
            except OSError:
                pass
        self.thread.join(timeout=1)
        self.listener.close()


def request_pipe(profile, request, timeout=100):
    settings = profile / "mcp.json"
    address = pipe_address(profile)
    config = json.loads(settings.read_text(encoding="utf-8"))
    if not config["enabled"]:
        raise ValueError("MCP disabled")
    with Client(address, family="AF_PIPE", authkey=config["token"].encode()) as connection:
        connection.send_bytes(json.dumps(request, ensure_ascii=False).encode())
        if not connection.poll(timeout):
            raise TimeoutError("Desktop MCP did not reply")
        return json.loads(connection.recv_bytes(RESPONSE_LIMIT))


def run_stdio(profile, stdin, stdout):
    for line in iter(lambda: stdin.readline(REQUEST_LIMIT + 1), ""):
        request = None
        try:
            if len(line.encode()) > REQUEST_LIMIT:
                raise ValueError("MCP request is too large")
            request = json.loads(line)
        except ValueError:
            response = error_response(None, "Invalid MCP request", -32700)
        else:
            # Stateless transports do not need to forward notifications.
            if isinstance(request, dict) and "id" not in request:
                continue
            try:
                response = request_pipe(profile, request)
            except (OSError, EOFError, ValueError, KeyError, AuthenticationError):
                response = error_response(request, "Open GH Release Fetch and enable its local MCP service.")
        if response is not None:
            stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            stdout.flush()
    return 0
