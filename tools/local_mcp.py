"""Authenticated, stateless Streamable HTTP transport for the desktop queue."""

import hmac
import ipaddress
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

VERSIONS = ("2025-11-25", "2025-06-18", "2025-03-26")
PRIVATE = tuple(map(ipaddress.ip_network, ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")))


class Server(ThreadingHTTPServer):
    def __init__(self, host, port, token, tools, invoke, *, source_url):
        self.token = token
        self.tools = tools
        self.invoke = invoke
        self.source_url = source_url
        super().__init__((host, port), Handler)

    def start(self):
        Thread(target=self.serve_forever, kwargs={"poll_interval": 0.1}, daemon=True).start()

    def stop(self):
        self.shutdown()
        self.server_close()


class Handler(BaseHTTPRequestHandler):
    def setup(self):
        self.request.settimeout(8)
        super().setup()

    def log_message(self, *_):
        pass

    def reply(self, status, body=None):
        payload = b"" if body is None else json.dumps(body, ensure_ascii=False).encode()
        self.send_response(status)
        if body is not None:
            self.send_header("Content-Type", "application/json; charset=utf-8")
        if status == 401:
            self.send_header("WWW-Authenticate", "Bearer")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        if payload:
            self.wfile.write(payload)

    def authorized(self):
        if self.path != "/mcp":
            self.reply(404)
            return False
        # Browser origins are never needed by native MCP clients. Reject them
        # before parsing any message to prevent browser-based rebinding.
        host = self.headers.get("Host", "")
        peer = ipaddress.ip_address(self.client_address[0])
        local = self.connection.getsockname()[0]
        hosts = {f"{local}:{self.server.server_port}"}
        if peer.is_loopback:
            hosts.add(f"localhost:{self.server.server_port}")
        if self.headers.get("Origin") is not None or host not in hosts or not (
            peer.is_loopback or any(peer in network for network in PRIVATE)
        ):
            self.reply(403)
            return False
        supplied = self.headers.get("Authorization", "").encode("utf-8")
        if not hmac.compare_digest(supplied, ("Bearer " + self.server.token).encode()):
            self.reply(401)
            return False
        version = self.headers.get("MCP-Protocol-Version")
        if version and version not in VERSIONS:
            self.reply(400)
            return False
        return True

    def do_GET(self):
        if self.authorized():
            self.reply(405)

    do_DELETE = do_GET

    def do_POST(self):
        if not self.authorized():
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 131072 or self.headers.get("Transfer-Encoding"):
                raise ValueError
            request = json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, TimeoutError):
            self.reply(400)
            return
        try:
            response = dispatch(request, self.server.tools, self.server.invoke, self.server.source_url)
        except ValueError:
            self.reply(400)
            return
        self.reply(202 if response is None else 200, response)


def dispatch(request, tools, invoke, source_url):
    if not isinstance(request, dict) or request.get("jsonrpc") != "2.0":
        raise ValueError("Invalid JSON-RPC request")
    method, params = request.get("method"), request.get("params", {})
    if "id" not in request:
        return None
    response = {"jsonrpc": "2.0", "id": request["id"]}
    if not isinstance(params, dict):
        response["error"] = {"code": -32602, "message": "Invalid params"}
    elif method == "initialize":
        version = params.get("protocolVersion")
        response["result"] = {
            "protocolVersion": version if version in VERSIONS else VERSIONS[0],
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "GH Release Fetch", "version": "1.0"},
            "instructions": f"Licensed under AGPL-3.0. Corresponding Source: {source_url}",
        }
    elif method == "ping":
        response["result"] = {}
    elif method == "tools/list":
        response["result"] = {"tools": list(tools.values())}
    elif method == "tools/call":
        name, arguments = params.get("name"), params.get("arguments", {})
        if not isinstance(name, str) or name not in tools or not isinstance(arguments, dict):
            response["error"] = {"code": -32602, "message": "Unknown tool or invalid arguments"}
        else:
            try:
                result = invoke(name, arguments)
                response["result"] = {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]}
            except Exception as exc:
                response["result"] = {"content": [{"type": "text", "text": str(exc)}], "isError": True}
    else:
        response["error"] = {"code": -32601, "message": "Method not found"}
    return response
